import json
import os
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class PageContext:
    name: str
    url: str
    search_context: List[Dict]

    @classmethod
    def from_dict(cls, obj):
        return cls(
            obj.get('name'),
            obj.get('url'),
            obj.get('search_context')
        )


class Page:
    def __init__(self, page_context: PageContext = None, **kwargs):
        if page_context:
            self.name = page_context.name
            self.url = page_context.url
            o = urlparse(page_context.url)
            self.domain = o.netloc
            self.search_context = page_context.search_context
            self.depth = len(page_context.search_context)
            self.followed_links = {}
            self.links = {}
            self.scrape()

        if kwargs:
            self.name = kwargs.get('name')
            self.url = kwargs.get('url')
            self.domain = kwargs.get('domain')
            self.search_context = kwargs.get('search_context')
            self.depth = len(self.search_context)
            self.followed_links = kwargs.get('followed_links')
            self.links = kwargs.get('links')

    @staticmethod
    def find_elements(url, **kwargs):
        response = requests.get(url)
        assert 200 <= response.status_code <= 299
        bs = BeautifulSoup(response.content, 'html.parser')
        return bs.find_all(**kwargs)

    def scrape(self):
        results = self.find_elements(self.url, **self.search_context[0])

        for result in results:
            anchor = result.find('a')
            if anchor:
                self.links.update({anchor.string: self.get_url(anchor.get('href'))})
            else:
                self.links.update({result.string: self.url})

        if self.depth > 1:
            for name, page in self.links.items():
                results = self.find_elements(page, **self.search_context[1])
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

    @staticmethod
    def slugify(in_str: str) -> str:
        replacements = [
            '/', '.', ',', ':', ' '
        ]
        for char in replacements:
            in_str = in_str.replace(char, '_')

        return in_str

    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'domain': self.domain,
            'search_context': self.search_context,
            'followed_links': self.followed_links,
            'links': self.links
        }

    @property
    def file_name(self):
        return os.path.join(BASE_DIR, f'{self.slugify(self.name)}.json')

    def write(self):
        with open(self.file_name, 'w') as file:
            json.dump(self.to_dict(), file)

    @classmethod
    def from_file(cls, page_name):
        with open(os.path.join(BASE_DIR, page_name), 'r') as file:
            obj_dict = json.load(file)

        return cls(**obj_dict)


class PageScraper:
    def __init__(self, pages: List = None):
        self.pages = []
        if pages is None:
            self.load_directory()
        else:
            for page in pages:
                self.scrape_page(page)

    def scrape_page(self, p: PageContext):
        obj = Page(p)
        obj.write()
        self.pages.append(obj)

    def load_directory(self):
        path = os.path.join(BASE_DIR, 'pages')
        for root, dirs, files in os.walk(path):
            for file in files:
                if '.json' in file:
                    self.pages.append(Page.from_file(f'pages/{file}'))


scraper = PageScraper()


if __name__ == '__main__':

    webpages = [
        PageContext('SouthPark DE', 'https://www.southpark.de/seasons/south-park', [{'name': 'li', 'attrs': {'role': 'menuitem'}}, {'name': 'li', 'class_': 'full-ep'}]),
        PageContext('SouthPark EN', 'https://www.southpark.de/en/seasons/south-park', [{'name': 'li', 'attrs': {'role': 'menuitem'}}, {'name': 'li', 'class_': 'full-ep'}])
    ]

    for page in webpages:
        scraper.scrape_page(page)
