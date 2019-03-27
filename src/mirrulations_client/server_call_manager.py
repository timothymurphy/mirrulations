import json
import requests


class ServerCallManager:

    def __init__(self, client_id, address):
        self.client_id = client_id
        self.base_url = 'https://' + address

    def make_work_call(self):
        return requests.get(self.base_url + '/get_work?client_id=' + self.client_id)

    def make_doc_return_call(self, file, json_dict):
        return requests.post(self.base_url + '/return_doc',
                             files={'file': file},
                             data={'json': json.dumps(json_dict)})

    def make_docs_return_call(self, file, json_dict):
        return requests.post(self.base_url + '/return_docs',
                             files={'file': file},
                             data={'json': json.dumps(json_dict)})
