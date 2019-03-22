import logging
import requests
import time

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='api_call_management.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'CLIENT'}
logger = logging.getLogger('tcpserver')


class APICallManager:

    def __init__(self, api_key):
        self.api_key = api_key

    class CallFailException(Exception):

        def __init__(self):
            logger.debug('EXCEPTION: %s', 'CallFailException: There seems to be an error with your API call',
                         extra=d)
            logger.warning('API call failed...')

    def make_call(self, url):

        pause = 0
        while pause < 51:

            result = requests.get(url)
            if result.status_code == 429:
                logger.debug('Exception: %s', 'api_call_mangement: Caught ApiCountZeroException. Waiting 1 hour.',
                             extra=d)
                logger.error('Error: ran out of API calls')
                time.sleep(3600)
            elif 300 < result.status_code < 400:
                logger.debug('Exception: %s',
                             'api_call_mangement: Caught TemporaryException, waiting 5 minutes. Current pause: ' +
                             str(pause), extra=d)
                logger.error('Error: waiting 5 minutes...')
                time.sleep(300)
                pause += 1
            elif 400 <= result.status_code < 600:
                logger.debug('Exception: %s', 'api_call_mangement: Caught PermanentException', extra=d)
                logger.error('Error with the API call')
                break
            else:
                return result

        logger.debug('Exception: %s', 'api_call_mangement: CallFailException for return docs', extra=d)
        logger.debug('Incomplete: %s', url, extra=d)
        logger.error('API call failed...')
        raise self.CallFailException

    def make_api_call_url(self, search_type, suffix):

        return 'https://api.data.gov/regulations/v3/' + search_type + '.json?api_key=' + self.api_key + suffix

    def make_document_call(self, document_id, attachment_number=None, content_type=None):
        return self.make_call(self.make_api_call_url('document',
                                                      '&documentId=' + document_id
                                                     + ('' if attachment_number is None
                                                         else '&attachmentNumber=' + str(attachment_number))
                                                     + ('' if content_type is None
                                                         else '&contentType=' + content_type)))

    def make_documents_call(self, counts_only=False, page_offset=None, results_per_page=None):
        return self.make_call(self.make_api_call_url('documents',
                                                     ('&countsOnly=1' if counts_only else '')
                                                     + ('' if page_offset is None
                                                         else '&po=' + str(page_offset))
                                                     + ('' if results_per_page is None
                                                         else '&rpp=' + str(results_per_page))))

    def make_docket_call(self, docket_id):
        return self.make_call(self.make_api_call_url('docket.json',
                                                      '&docketId=' + docket_id))


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
