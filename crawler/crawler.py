import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import weaviate
import spacy
import re

class UniversityCrawler:
    def __init__(self, start_urls, max_depth=3, batch_size=10):
        self.start_urls = start_urls
        self.visited_urls = set()
        self.max_depth = max_depth
        self.batch_size = batch_size
        self.batch_data = []
        self.client = weaviate.Client('http://localhost:8080')
        self.nlp = spacy.load("en_core_web_sm")
        self.client.batch.configure(batch_size=100, dynamic=True)
    def crawl(self):
        for url in self.start_urls:
            self.process_url(url, 0)

    def process_url(self, url, depth):
        if url in self.visited_urls or depth > self.max_depth:
            return
        self.visited_urls.add(url)
        print(f"Crawling URL (depth {depth}): {url}")
        soup = self.fetch_url(url)
        if not soup:
            return
        if self.is_relevant_url(url):
            self.process_page_content(url, soup, depth)
        if depth < self.max_depth:
            self.crawl_links(soup, url, depth)

    def fetch_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def process_page_content(self, url, soup, depth):
        content = ' '.join(soup.get_text().split())
        data_object = {
            "content": content,
            "url": url,
            "depth": depth
        }

        # Add the data object to the batch
        print(self.client.batch.add_data_object(data_object, class_name="UniversityPage"))

    def preprocess_text(self, text):
        doc = self.nlp(text)
        result = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space:
                result.append(token.lemma_)
        return ' '.join(result)

    def extract_relevant_content(self, soup):
        article_body = soup.find('article')
        return article_body.get_text() if article_body else ''

    def crawl_links(self, soup, current_url, depth):
        for link in soup.find_all('a', href=True):
            next_link = urljoin(current_url, link['href'])
            if self.is_valid_url(next_link) and self.link_has_relevant_text(link):
                self.process_url(next_link, depth + 1)

    def link_has_relevant_text(self, link):
        text = link.get_text()
        keywords = ['admissions', 'apply', 'application', 'program', 'course']
        return any(keyword in text.lower() for keyword in keywords)

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and not self.is_off_topic(url)

    def is_off_topic(self, url):
        off_topic_patterns = ['/privacy', '/login', '/help', '/settings', '/accounts']
        return any(pattern in url for pattern in off_topic_patterns)

    def is_relevant_url(self, url):
        keywords = ['admissions', 'apply', 'application', 'program', 'course']
        return any(keyword in url for keyword in keywords)
    def finalize_batch(self):
        # Flush any remaining objects in the batch
        self.client.batch.flush()
    def insert_batch_data(self):
        if self.batch_data:
            try:
                for data_object in self.batch_data:
                    self.client.batch.add_data_object(data_object, class_name="UniversityPage")
                # Execute the batch operation
                self.client.batch.create_objects()
                print("Batch data inserted successfully.")
                self.client.batch = weaviate.batch.Batch(self.client)  # Reset the batch object
            except Exception as e:
                print(f"Error inserting batch data into Weaviate: {e}")
            finally:
                # Clear the batch data list after attempting to insert
                self.batch_data = []



start_urls = [
"https://college.harvard.edu/admissions",
"https://admission.stanford.edu",
"https://mitadmissions.org",
# Add more URLs as needed
]
crawler = UniversityCrawler(start_urls)
crawler.crawl()

