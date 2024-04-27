import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

class UniversityCrawler:
    def __init__(self, start_urls, max_depth=3, output_file='../backend/data.json'):
        self.start_urls = start_urls
        self.allowed_domains = {urlparse(url['url']).netloc for url in start_urls}
        self.visited_urls = set()
        self.max_depth = max_depth
        self.output_file = output_file
        self.batch_data = []
        self.data_id = 1  # Initialize data ID counter

    def crawl(self):
        for entry in self.start_urls:
            self.process_url(entry['url'], entry['university_name'], 0)
        self.save_data_to_file()

    def process_url(self, url, university_name, depth):
        if url in self.visited_urls or depth > self.max_depth:
            return
        self.visited_urls.add(url)
        print(f"Crawling URL (depth {depth}): {url}")
        soup = self.fetch_url(url)
        if not soup:
            return
        if self.is_relevant_url(url):
            self.process_page_content(url, university_name, soup)
        if depth < self.max_depth:
            self.crawl_links(soup, url, university_name, depth)

    def fetch_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def process_page_content(self, url, university_name, soup):
        content = soup.get_text(separator=' ', strip=True)
        data_object = {
            "id": self.data_id,
            "url": url,
            "university_name": university_name,
            "content": content
        }
        self.data_id += 1
        self.batch_data.append(data_object)

    def save_data_to_file(self):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.batch_data, f, ensure_ascii=False, indent=4)

    def crawl_links(self, soup, current_url, university_name, depth):
        for link in soup.find_all('a', href=True):
            next_link = urljoin(current_url, link['href'])
            if self.is_valid_url(next_link):
                self.process_url(next_link, university_name, depth + 1)

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        return parsed_url.scheme in ['http', 'https'] and domain in self.allowed_domains and not any(pattern in url for pattern in ['/privacy', '/login', '/help', '/settings', '/accounts'])

    def is_relevant_url(self, url):
        return any(keyword in url for keyword in ['admissions', 'apply', 'application', 'program', 'course'])

start_urls = [
    {"url": "https://college.harvard.edu/admissions", "university_name": "Harvard University"},
    {"url": "https://admission.stanford.edu", "university_name": "Stanford University"},
    {"url": "https://mitadmissions.org", "university_name": "MIT"}
]

crawler = UniversityCrawler(start_urls)
crawler.crawl()
