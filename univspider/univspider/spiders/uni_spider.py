import scrapy
import json
import os
import re
from bs4 import BeautifulSoup


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
        
        title = response.css('h1::text').get()
        title = title.strip() if title else ''
        
        content = response.xpath('//body//text()').getall()  # Obtener todo el texto dentro del cuerpo
        content = ' '.join(content)  # Convertir la lista de strings a un solo string
        content = re.sub(r'\s+', ' ', content)  # Eliminar espacios en blanco adicionales

        content = BeautifulSoup(content).text
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
                if self.is_edu_link(link):
                    yield response.follow(link, meta={'id': university_id, 'university_name': university_name, 'depth': depth + 1}, callback=self.parse)

    def save_item(self, item, university_id):
        filename = f'archivos_json/university_{university_id}.json'
        with open(filename, 'a', encoding='utf-8') as f:
            if os.stat(filename).st_size == 0:
                f.write("[")
            else:
                f.write(",\n")
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
    
    def is_edu_link(self, link):
        pattern = r'^https?://(?:[a-zA-Z0-9-]+\.)+(?:edu)/?'
        return re.match(pattern, link)
