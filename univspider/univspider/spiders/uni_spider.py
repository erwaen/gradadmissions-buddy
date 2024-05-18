import scrapy
import json
import os
import datetime
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class UniversitySpider(scrapy.Spider):
    name = 'university'
    start_urls = [
        ("https://cs.uchicago.edu/mpcs", "University of Chicago"),
        ("https://gradschool.princeton.edu/academics/degrees-requirements/fields-study/computer-science", "Princeton University"),
        ("https://gradschool.cornell.edu/academics/fields-of-study/subject/computer-science/computer-science-ms-ithaca/", "Cornell University"),
        ("https://www.cs.columbia.edu/education/ms/", "Columbia University"),
        ("https://www.cs.jhu.edu/academic-programs/graduate-studies/mse-programs/", "Johns Hopkins University"),
        ("https://www.washington.edu/admissions/", "University of Washington"),
        ("https://www.cs.rochester.edu/graduate/masters-program.html", "University of Rochester"),
        ("https://college.harvard.edu/admissions", "Harvard University"),
        ("https://www.stanford.edu/admission/", "Stanford University"),
        ("https://www.upenn.edu/admissions","University of Pensylvania")
    ]
    max_depth_per_university = 2
    visited_urls = set()
    document_counter = {}  # Contador de documentos por universidad
    
    def start_requests(self):
        universities_arg = getattr(self, 'universities', None)
        universities_to_scrape = universities_arg.split(',') if universities_arg else None

        for idx, (url, university_name) in enumerate(self.start_urls, start=1):
            if universities_to_scrape is None or str(idx) in universities_to_scrape:
                yield scrapy.Request(url, meta={'id': idx, 'university_name': university_name, 'depth': 1}, callback=self.parse)
    
    def parse(self, response):
        university_id = response.meta['id']
        university_name = response.meta['university_name']

        if response.status != 200:
            self.log(f"Failed to retrieve {response.url} (status: {response.status})")
            return
        
        #title = response.css('h1::text').get()
        title = response.css('h1::text, h2::text').get()
        title = title.strip() if title else ''
        
        content = self.fetch_text_from_url(response.url)
        if not content:
            self.log(f"No content fetched from {response.url}")
            return

        content = BeautifulSoup(content, 'html.parser').text
        if content:
            item = {
                'id': university_id,
                'date': datetime.datetime.now().isoformat(),
                'url': response.url,
                'university_name': university_name,
                'title': title,
                'content': content
            }
            self.save_item(item, university_id)
        else:
            self.log(f"No text content found in {response.url}")

        depth = response.meta.get('depth', 1)
        if depth < self.max_depth_per_university:
            links = response.css('a::attr(href)').getall()
            for link in links:
                if self.is_edu_link(link):
                    next_link = response.urljoin(link)
                    if next_link not in self.visited_urls:
                        self.visited_urls.add(next_link) 
                        yield response.follow(link, meta={'id': university_id, 'university_name': university_name, 'depth': depth + 1}, callback=self.parse)

    def fetch_text_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.find('body')
            if body:
                return self.clean_text(body.get_text(separator=' ', strip=True))
            else:
                return None
        except requests.RequestException as e:
            self.log(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text):
        cleaned_text = re.sub(r'\{\{.*?\}\}', '', text)
        cleaned_text = re.sub(r'\{\{.*?$', '', cleaned_text) 
        cleaned_text = re.sub(r'Add to GMail Close', '', cleaned_text)
        return cleaned_text.strip()

    def save_item(self, item, university_id):
        directory = f'dataset/university{university_id}'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Incrementar el contador de documentos para esta universidad
        if university_id not in self.document_counter:
            self.document_counter[university_id] = 1
        else:
            self.document_counter[university_id] += 1

        # Generar el nombre del archivo
        document_number = self.document_counter[university_id]
        filename = f'{directory}/documento{document_number}.json'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)

    def closed(self, reason):
        self.log('Spider closed.')
    
    def is_edu_link(self, link):
        pattern = r'^https?://(?:[a-zA-Z0-9-]+\.)+(?:edu)/?'
        return re.match(pattern, link)
