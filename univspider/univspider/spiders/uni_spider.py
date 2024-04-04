import scrapy
import json
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class UniversitySpider(CrawlSpider):
    name = 'university'
    allowed_domains = ['cs.uchicago.edu', 'gradschool.princeton.edu', 'gradschool.cornell.edu',
                       'cs.columbia.edu', 'cs.jhu.edu', 'cse.engin.umich.edu', 'cs.rochester.edu']
    start_urls = [
        ("https://cs.uchicago.edu/mpcs", "University of Chicago"),
        ("https://gradschool.princeton.edu/academics/degrees-requirements/fields-study/computer-science", "Princeton University"),
        ("https://gradschool.cornell.edu/academics/fields-of-study/subject/computer-science/computer-science-ms-ithaca/", "Cornell University"),
        ("https://www.cs.columbia.edu/education/ms/", "Columbia University"),
        ("https://www.cs.jhu.edu/academic-programs/graduate-studies/mse-programs/", "Johns Hopkins University"),
        ("https://cse.engin.umich.edu/academics/graduate/", "University of Michigan"),
        ("https://www.cs.rochester.edu/graduate/masters-program.html", "University of Rochester")
    ]

    rules = (
        Rule(LinkExtractor(allow=()), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {
            'id': response.meta['id'],
            'url': response.url,
            'university_name': response.meta['university_name'],
            'content': ' '.join(response.css('p::text, h1::text, h2::text').getall())
        }
        yield item

    def start_requests(self):
        for idx, (url, university_name) in enumerate(self.start_urls):
            yield scrapy.Request(url, meta={'id': idx + 1, 'university_name': university_name}, callback=self.parse_item)

    def closed(self, reason):
        json_data = []
        for item in self.items:
            json_item = {
                'id': item['id'],
                'university_name': item['university_name'],
                'url': item['url'],
                'content': item['content']
            }
            json_data.append(json_item)

        with open('university_data.json', 'w') as f:
            json.dump(json_data, f, indent=4)  # Agrega indent=4 para formatear con sangrías y mejorar la legibilidad
