import os
import subprocess
from typing import Tuple

import selenium.common
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.support.wait import WebDriverWait


class AppServer:
    def __init__(self):
        self.data = None
        command = f'id -u {os.environ.get("USER")}'
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        self.user, error = proc.communicate()
        self.user = int(self.user)
        self.user = os.environ.get("USER")
        self.proc = None
        self.app = os.environ.get('MIRROR_APPLICATION', 'chromium')
        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument(f'--user-data-dir=/home/{self.user}/.config/chromium/')
        self.chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.needs_recreate = False
        self.driver = None

    def spawn_window(self, website: str = 'https://google.com') -> None:
        """ opens application window """
        if self.driver and self.needs_recreate:
            self.driver.quit()
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(website)
        self.needs_recreate = True
        try:
            # South Park
            WebDriverWait(self.driver, 5).until(element_to_be_clickable((By.CLASS_NAME, 'edge-placeholder-button'))).click()
            WebDriverWait(self.driver, 15).until(element_to_be_clickable((By.CLASS_NAME, 'edge-gui-fullscreen-button'))).click()
        except selenium.common.exceptions.TimeoutException:
            # YouTube
            def manage_popup():
                WebDriverWait(self.driver, 5)
                elems = self.driver.find_elements_by_xpath('//paper-button')
                elems = filter(lambda x: x.text == 'NO, THANKS', elems)
                elems = [i for i in elems]
                assert len(elems) == 1, f'Did expect less objects. Got {elems}'

                elem = elems[0]
                elem.click()
                WebDriverWait(self.driver, 10).until(element_to_be_clickable((By.XPATH, '//div#introAgreeButton'))).click()

            manage_popup()
            WebDriverWait(self.driver, 5).until(element_to_be_clickable((By.CLASS_NAME, 'html5-video-player'))).click()
            while True:
                try:
                    WebDriverWait(self.driver, 15).until(element_to_be_clickable((By.CLASS_NAME, 'ytp-ad-skip-button-text'))).click()
                except ElementClickInterceptedException:
                    pass
                except NoSuchElementException:
                    break
            WebDriverWait(self.driver, 15).until(element_to_be_clickable((By.CLASS_NAME, 'ytp-fullscreen-button'))).click()

    def fetch(self):
        """ reloads list of current running processes """
        self.data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]

    def find(self, name: str) -> Tuple[int, list]:
        """ find process by name (uses iLike matches)"""
        for elem in self.data:
            if name in elem[1]:
                return elem


server = AppServer()
