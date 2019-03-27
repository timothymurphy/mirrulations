import requests
import time

from mirrulations_core import LOGGER


class APICallManager:

    def __init__(self, api_key):
        self.api_key = api_key

    class CallFailException(Exception):

        def __init__(self):
            LOGGER.warning('API call failed...')

    def make_api_call_url(self, search_type, suffix):
        return 'https://api.data.gov/regulations/v3/' + search_type + '.json?api_key=' + self.api_key + suffix

    def make_docket_call_url(self, docket_id):
        return self.make_api_call_url('docket', '&docketId=' + docket_id)

    def make_document_call_url(self, document_id, attachment_number=None, content_type=None):
        return self.make_api_call_url('document',
                                      '&documentId=' + document_id
                                      + ('' if attachment_number is None else '&attachmentNumber='
                                                                              + str(attachment_number))
                                      + ('' if content_type is None else '&contentType=' + content_type))

    def make_documents_call_url(self, counts_only=False, page_offset=None, results_per_page=None):
        return self.make_api_call_url('documents',
                                      ('&countsOnly=1' if counts_only else '')
                                      + ('' if page_offset is None else '&po=' + str(page_offset))
                                      + ('' if results_per_page is None else '&rpp=' + str(results_per_page)))

    def make_call(self, url):

        pause = 0
        while pause < 51:

            result = requests.get(url)

            if result.status_code == 429:
                LOGGER.error('Error: ran out of API calls')
                time.sleep(3600)

            elif 300 < result.status_code < 400:
                LOGGER.error('Error: waiting 5 minutes...')
                time.sleep(300)
                pause += 1

            elif 400 <= result.status_code < 600:
                LOGGER.error('Error with the API call')
                break

            else:
                LOGGER.warning('API call successfully made')
                return result

        LOGGER.error('API call failed...')
        raise self.CallFailException

    def make_docket_call(self, docket_id):
        return self.make_call(self.make_docket_call_url(docket_id))

    def make_document_call(self, document_id, attachment_number=None, content_type=None):
        return self.make_call(self.make_document_call_url(document_id, attachment_number, content_type))

    def make_documents_call(self, counts_only=False, page_offset=None, results_per_page=None):
        return self.make_call(self.make_documents_call_url(counts_only, page_offset, results_per_page))


def verify_key(key_input):

    class CannotConnectError(Exception):
        print('Unable to connect!\n'
              'We weren\'t able to connect to regulations.gov.\n'
              'Please try again later.')
        exit(3)

    class InvalidKeyError(Exception):
        print('Invalid API key!\n'
              'Your API key is invalid.\n'
              'Please visit\n'
              'https://regulationsgov.github.io/developers/\n'
              'for an API key.')
        exit(4)

    try:
        with requests.get('https://api.data.gov/regulations/v3/documents.json?api_key=' + key_input) as r:
            if r.status_code == 403:
                raise CannotConnectError
            elif r.status_code > 299 and r.status_code != 429:
                raise InvalidKeyError
            else:
                print('Success!\n'
                      'You are successfully logged in.')
                return None
    except requests.ConnectionError:
        raise CannotConnectError
