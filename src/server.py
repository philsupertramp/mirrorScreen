import os
import subprocess
from typing import Tuple


class AppServer:
    def __init__(self):
        self.data = None
        command = f'id -u {os.environ.get("USER")}'
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        self.user, error = proc.communicate()
        self.user = int(self.user)
        self.user = os.environ.get("USER")
        self.proc = None
        self.app = 'chromium'

    def spawn_window(self, website: str = 'https://google.com') -> Tuple:
        """ opens application window """
        command = f'sudo -H -u {self.user} {self.app} {website}'
        self.proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        return self.proc.communicate()

    def fetch(self):
        """ reloads list of current running processes """
        self.data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) for x in os.popen('ps h -eo pid:1,command')]]

    def find(self, name: str) -> Tuple[int, list]:
        """ find process by name (uses iLike matches)"""
        for elem in self.data:
            if name in elem[1]:
                return elem


server = AppServer()
