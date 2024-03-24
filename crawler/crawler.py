import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from dotenv import load_dotenv

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import weaviate
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
class UniversityCrawler:
    def __init__(self, start_urls, max_depth=3):
        self.start_urls = start_urls
        self.visited_urls = set()
        self.max_depth = max_depth
        self.client = weaviate.connect_to_local(host="localhost",headers={"X-Openai-Api-Key" : OPENAI_API_KEY})
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
        content = soup.get_text()

        university_page_collection = self.client.collections.get("UniversityPage")
        uuid = university_page_collection.data.insert({
        "url": url,
        "content": content,
        "depth": depth
        })
        print(f"Data inserted with UUID: {uuid}")

    def url_to_filename(self, url):
        filename = urlparse(url).netloc + urlparse(url).path
        filename = filename.replace('/', '_').replace(':', '_').strip('_')
        return f"{filename}.txt"

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
    "http://admissions.berkeley.edu",
    "https://www.ox.ac.uk/admissions",
    "https://www.undergraduate.study.cam.ac.uk",
    "https://www.imperial.ac.uk/study/ug",
    "https://future.utoronto.ca/apply",
    "https://you.ubc.ca/admissions",
    "https://www.mcgill.ca/undergraduate-admissions",
    "https://www.anu.edu.au/study/apply",
    "https://www.sydney.edu.au/study/how-to-apply.html",
    "https://study.unimelb.edu.au/how-to-apply",
    "https://ethz.ch/en/studies/prospective-students.html",
    "https://www.sorbonne-universite.fr/en/admissions",
    "https://www.lmu.de/en/study/application-and-acceptance/index.html",
    "https://www.nus.edu.sg/oam/apply-to-nus",
    "http://www.tsinghua.edu.cn/publish/thu2018en/newthuen_cnt/admissions/admissions-1.html",
    "https://www.u-tokyo.ac.jp/en/prospective-students/admissions.html"
]

    crawler = UniversityCrawler(start_urls)
    crawler.crawl()
