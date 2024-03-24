import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import weaviate
from dotenv import load_dotenv

class UniversityCrawler:
    def __init__(self, start_urls, max_depth=3):
        self.start_urls = start_urls
        self.visited_urls = set()
        self.max_depth = max_depth
        load_dotenv()

        self.client = weaviate.Client('http://localhost:8080')

    def crawl(self):
        for url in self.start_urls:
            self.process_url(url, 0)

    def process_url(self, url, depth):
        if url in self.visited_urls or depth > self.max_depth:
            return

        if not self.is_relevant_url(url):
            return

        print(f"Crawling URL (depth {depth}): {url}")
        self.visited_urls.add(url)

        soup = self.fetch_url(url)
        if soup is None:
            return

        self.process_page_content(url, soup, depth)

        if depth < self.max_depth:
            for link in soup.find_all('a', href=True):
                next_link = urljoin(url, link['href'])
                if self.is_valid_url(next_link):
                    self.process_url(next_link, depth + 1)

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

        try:
            response = self.client.data_object.create(data_object, "UniversityPage")
            if 'id' in response:
                print("Data inserted successfully.")
        except Exception as e:
            print(f"Error inserting data into Weaviate: {e}")


    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and not self.is_off_topic(url)

    def is_off_topic(self, url):
        off_topic_patterns = ['/privacy', '/login', '/help', '/settings', '/accounts']
        return any(pattern in url for pattern in off_topic_patterns)

    def is_relevant_url(self, url):
        keywords = ['admissions', 'apply', 'application']
        return any(keyword in url for keyword in keywords)

if __name__ == "__main__":
    start_urls = [
        "https://college.harvard.edu/admissions",
        "https://admission.stanford.edu",
        "https://mitadmissions.org",
    ]

    crawler = UniversityCrawler(start_urls)
    crawler.crawl()
