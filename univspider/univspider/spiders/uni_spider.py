import scrapy
import json
import os

class UniversitySpider(scrapy.Spider):
    name = 'university'
    start_urls = [
        ("https://cs.uchicago.edu/mpcs", "University of Chicago"),
        ("https://gradschool.princeton.edu/academics/degrees-requirements/fields-study/computer-science", "Princeton University"),
        ("https://gradschool.cornell.edu/academics/fields-of-study/subject/computer-science/computer-science-ms-ithaca/", "Cornell University"),
        ("https://www.cs.columbia.edu/education/ms/", "Columbia University"),
        ("https://www.cs.jhu.edu/academic-programs/graduate-studies/mse-programs/", "Johns Hopkins University"),
        ("https://cse.engin.umich.edu/academics/graduate/", "University of Michigan"),
        ("https://www.cs.rochester.edu/graduate/masters-program.html", "University of Rochester")
    ]
    max_depth_per_university = 2

    def parse(self, response):
        university_id = response.meta['id']
        university_name = response.meta['university_name']
        
        # Extraer el título de la página (texto del primer h1)
        title = response.css('h1::text').get()
        # Limpiar el título de caracteres de nueva línea y tabulación
        title = title.strip() if title else ''

        # Extraer texto del cuerpo de la respuesta y eliminar caracteres de nueva línea y tabulación
        content = response.css('body').xpath('string()').get()
        content = content.replace('\n', '').replace('\t', '')

        if content:
            item = {
                'id': university_id,
                'url': response.url,
                'university_name': university_name,
                'title': title,
                'content': content
            }
            self.save_item(item, university_id)

        # Guardar contenido de todos los enlaces con la misma estructura
        depth = response.meta.get('depth', 1)
        if depth < self.max_depth_per_university:
            links = response.css('a::attr(href)').getall()
            for link in links:
                yield response.follow(link, meta={'id': university_id, 'university_name': university_name, 'depth': depth + 1}, callback=self.parse)

    def save_item(self, item, university_id):
        filename = f'archivos_json/university_{university_id}.json'
        with open(filename, 'a', encoding='utf-8') as f:
            if os.stat(filename).st_size == 0:
                f.write("[")
            else:
                f.write(",")
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")
        
    def start_requests(self):
        for idx, (url, university_name) in enumerate(self.start_urls, start=1):
            yield scrapy.Request(url, meta={'id': idx, 'university_name': university_name, 'depth': 1}, callback=self.parse)

    def closed(self, reason):
        for idx, _ in enumerate(self.start_urls, start=1):
            filename = f'archivos_json/university_{idx}.json'
            with open(filename, 'a', encoding='utf-8') as f:
                f.write("]")
        self.log('Spider closed.')
