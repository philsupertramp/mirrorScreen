# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import subprocess
import sys
from typing import Tuple

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template

app = Flask(__name__)


class WindowServer:
    def __init__(self):
        self.data = None
        command = f'id -u {os.environ.get("USER")}'
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        self.user, error = proc.communicate()
        self.user = int(self.user)
        self.user = os.environ.get("USER")
        self.proc = None

    def spawn_window(self, website: str = 'https://google.com') -> Tuple:
        command = f'sudo -H -u {self.user} chromium {website}'
        self.proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        return self.proc.communicate()

    def fetch(self):
        self.data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]

    def find(self, name: str) -> Tuple[int, list]:
        for elem in self.data:
            if name in elem[1]:
                return elem


server = WindowServer()


class Page:
    def __init__(self, url):
        self.url = url
        self.scrape()

    def scrape(self):
        response = requests.get(self.url)
        bs = BeautifulSoup(response.content, 'html.parser')


class PageScraper:
    def __init__(self):
        self.pages = []

    def scrape_page(self, url: str = 'https://www.southpark.de/seasons/south-park'):
        self.pages.append(Page(url))


webpages = [
    'https://www.southpark.de/seasons/south-park',
    'https://www.southpark.de/en/seasons/south-park'
]

scraper = PageScraper()
for page in webpages:
    scraper.scrape_page(page)


@app.route('/')
def run_command():
    server.fetch()
    return render_template('frontend.html')


@app.route('/open/', methods=['POST'])
def open_site():
    if request.args.get('url'):
        server.spawn_window(request.args.get('url'))

    return 'Ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

