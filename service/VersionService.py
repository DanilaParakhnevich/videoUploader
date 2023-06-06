import os
import requests


class VersionService(object):

    def __init__(self):
        file = open(f'{os.path.abspath("version.txt")}', "r")
        self.version = file.readline()
        file.close()

    def get_current_version(self):
        return requests.request(method='get', url='http://bvu.buxarnet.ru/version.txt').text.strip()

    def get_current_client_version(self):
        return self.version
