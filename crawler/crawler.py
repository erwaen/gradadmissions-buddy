import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
class UniversityCrawler:
    def __init__(self, start_urls, cookies=None, delay=1.0):
        self.start_urls = start_urls
        self.session = requests.Session()
        if cookies:
            self.session.cookies.update(cookies)
        self.visited_urls = set()
        self.delay = delay
        self.output_dir = 'crawled_data'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def crawl(self):
        for url in self.start_urls:
            self.process_url(url)

    def process_url(self, url):
        if url in self.visited_urls or not self.is_valid_url(url):
            return
        print(f"Crawling URL: {url}")
        self.visited_urls.add(url)

        soup = self.fetch_url(url)
        if soup is None:
            return

        if self.is_relevant_page(url, soup):
            self.process_page_content(url, soup)

        for link in soup.find_all('a', href=True):
            next_link = urljoin(url, link['href'])
            if self.is_valid_url(next_link) and next_link not in self.visited_urls:
                self.process_url(next_link)

    def fetch_url(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def is_relevant_page(self, url, soup):
        keywords = ['admission', 'apply', 'application']
        return any(keyword in url.lower() for keyword in keywords)

    def process_page_content(self, url, soup):
        print(f"Processing content from {url}")

        # Extract specific data from the page (for demonstration, we'll just use the entire text)
        page_content = soup.get_text()

        # Save the content to a file
        filename = self.url_to_filename(url)
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(page_content)
        print(f"Saved content to {file_path}")
    def url_to_filename(self, url):
        """
        Converts a URL into a filename-safe string
        """
        # Simplify the URL into a filename-friendly format
        filename = urlparse(url).netloc + urlparse(url).path
        filename = filename.replace('/', '_').replace(':', '_').strip('_')
        return filename + '.txt'
    
    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https']

if __name__ == "__main__":
    start_urls = [
        "https://www.harvard.edu/admissions",  # Add more university homepages here
        "https://www.stanford.edu/admission"]
    cookies = {'sessionid': '123abc'}  # Example cookie, use actual cookies as needed
    crawler = UniversityCrawler(start_urls, cookies=cookies)
    crawler.crawl()
