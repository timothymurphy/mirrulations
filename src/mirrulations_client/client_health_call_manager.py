import requests


class ClientHealthCallManager:

    def __init__(self):
        self.base_url = 'https://hc-ping.com/457a1034-83d4-4a62-8b69-c71060db3a08'

    def make_call(self):
        requests.get(self.base_url)

    def make_fail_call(self):
        requests.get(self.base_url + '/fail')
