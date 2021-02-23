import os
import subprocess
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By


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
        self.driver = webdriver.Chrome()
        self.needs_recreate = False

    def spawn_window(self, website: str = 'https://google.com') -> None:
        """ opens application window """
        if self.driver and self.needs_recreate:
            self.driver.close()
        self.driver.get(website)
        self.needs_recreate = True
        self.driver.implicitly_wait(5)
        self.driver.find_element(By.CLASS_NAME, 'edge-placeholder-button').click()
        self.driver.find_element(By.CLASS_NAME, 'edge-gui-fullscreen-button').click()

    def fetch(self):
        """ reloads list of current running processes """
        self.data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]

    def find(self, name: str) -> Tuple[int, list]:
        """ find process by name (uses iLike matches)"""
        for elem in self.data:
            if name in elem[1]:
                return elem


server = AppServer()
