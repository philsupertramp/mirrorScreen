from dataclasses import dataclass
from typing import Tuple, Dict, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class PageContext:
    name: str
    url: str
    search_context: List[Dict]


class Page:
    def __init__(self, context: PageContext):
        self.name = context.name
        self.url = context.url
        o = urlparse(context.url)
        self.domain = o.netloc
        self.search_context = context.search_context
        self.depth = len(context.search_context)
        self.followed_links = {}
        self.links = {}
        self.scrape()

    def scrape(self):
        response = requests.get(self.url)
        assert 200 <= response.status_code <= 299
        bs = BeautifulSoup(response.content, 'html.parser')
        results = bs.find_all(**self.search_context[0])
        for result in results:
            anchor = result.find('a')
            if anchor:
                self.links.update({anchor.string: self.get_url(anchor.get('href'))})
            else:
                self.links.update({result.string: self.url})

        if self.depth > 1:
            for name, page in self.links.items():
                response = requests.get(page)
                assert 200 <= response.status_code <= 299
                bs = BeautifulSoup(response.content, 'html.parser')

                results = bs.find_all(**self.search_context[1])
                self.followed_links[name] = {}
                for result in results:
                    anchor = result.find('a')
                    if anchor:
                        header = anchor.find(class_='header')
                        self.followed_links[name].update(
                            {header.string: self.get_url(anchor.get('href'))}
                        )

    def get_url(self, sub):
        if self.domain.endswith('/') or sub.startswith('/'):
            return f'https://{self.domain}{sub}'
        return f'https://{self.domain}/{sub}'


class PageScraper:
    def __init__(self, pages):
        self.pages = []
        for page in pages:
            self.scrape_page(page)

    def scrape_page(self, page: PageContext):
        self.pages.append(Page(page))


webpages = [
    PageContext('SouthPark DE', 'https://www.southpark.de/seasons/south-park', [{'name': 'li', 'attrs': {'role': 'menuitem'}}, {'name': 'li', 'class_': 'full-ep'}]),
    PageContext('SouthPark EN', 'https://www.southpark.de/en/seasons/south-park', [{'name': 'li', 'attrs': {'role': 'menuitem'}}, {'name': 'li', 'class_': 'full-ep'}])
]


scraper = PageScraper(webpages)
