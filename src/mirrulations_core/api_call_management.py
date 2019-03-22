import logging
import requests
import time

key = 0

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='api_call_management.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'CLIENT'}
logger = logging.getLogger('tcpserver')


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


def make_url(search_type, suffix, url='https://api.data.gov/regulations/v3/'):
    return url + search_type + '.json?api_key=' + key + suffix


def get_document_url(document_id, attachment_number=None, content_type=None):
    return make_url('document', '&documentId=' + document_id
                                + ('' if attachment_number is None else '&attachmentNumber=' + str(attachment_number))
                                + ('' if content_type is None else '&contentType=' + content_type))


def get_documents_url(counts_only=False, page_offset=None, results_per_page=None):
    return make_url('documents.json', ''
                                      + ('&countsOnly=1' if counts_only else '')
                                      + ('' if page_offset is None else '&po=' + str(page_offset))
                                      + ('' if results_per_page is None else '&rpp=' + str(results_per_page)))


def get_docket_url(docket_id):
    return make_url('docket.json', '&docketId=' + docket_id)


def send_call(url):
    """
    Sends an API call to regulations.gov
    Raises exceptions if it is not a valid API call
    When a 300 status code is given, return a temporary exception so the user can retry the API call
    When a 429 status code is given, the user is out of API calls and must wait an hour to make more
    When 400 or 500 status codes are given there is a problem with the API connection
    :param url: the url that will be used to make the API call
    :return: returns the json format information of the documents
    """
    logger.warning('Making API call...')
    result = requests.get(url)
    if result.status_code == 429:
        logger.debug('Exception: %s', 'ApiCountZeroException for return docs', extra=d)
        logger.warning('API call failed')
        raise ApiCountZeroException
    if 300 <= result.status_code < 400:
        logger.debug('Exception: %s', 'TemporaryException for return docs', extra=d)
        logger.warning('API call failed')
        raise TemporaryException
    if 400 <= result.status_code < 600:
        logger.debug('Exception: %s', 'PermanentException for return docs', extra=d)
        logger.warning('API call failed')
        raise PermanentException
    logger.warning('API call successfully made')
    return result


def api_call(url):
    """
    If there were no errors in making an API call, get the result.
    If the user's ApiCount is zero, sleep for one hour to refresh the calls.
    If a Temporary error occurred, sleep for 5 minutes and try again.
    Do this 50 times, and if it continues to fail, raise a CallFailException.
    If a Permanent error occurs, raise a CallFailException.
    :param url: the url that will be used to make the API call
    :return: returns the resulting information of the documents
    """

    logger.debug('Call Successful: %s', 'api_call_mangement: starting API Call Manager', extra=d)
    logger.info('Managing API call...')

    pause = 0
    while pause < 51:
        try:
            return send_call(url)
        except ApiCountZeroException:
            logger.debug('Exception: %s', 'api_call_mangement: Caught ApiCountZeroException. Waiting 1 hour.', extra=d)
            logger.error('Error: ran out of API calls')
            time.sleep(3600)
        except TemporaryException:
            logger.debug('Exception: %s',
                         'api_call_mangement: Caught TemporaryException, waiting 5 minutes. Current pause: ' +
                         str(pause), extra=d)
            logger.error('Error: waiting 5 minutes...')
            time.sleep(300)
            pause += 1
        except PermanentException:
            logger.debug('Exception: %s', 'api_call_mangement: Caught PermanentException', extra=d)
            logger.error('Error with the API call')
            break
    logger.debug('Exception: %s', 'api_call_mangement: CallFailException for return docs', extra=d)
    logger.debug('Incomplete: %s', url, extra=d)
    logger.error('API call failed...')
    raise CallFailException


class ApiCountZeroException(Exception):
    """
    Raise an exception if the user is out of API calls
    """
    def __init__(self):
        logger.debug('EXCEPTION: %s', 'ApiCountZeroException: You have used all of your api calls', extra=d)
        logger.error('Error - ran out of API calls')


class TemporaryException(Exception):
    """
    Raise an exception if there is an error communicating with either the work server or regulations
    """
    def __init__(self):
        logger.debug('EXCEPTION: %s', 'TemporaryException: There seems to be a connection error', extra=d)
        logger.error('Error connecting to API')


class PermanentException(Exception):
    """
    Raise an exception if there is an error with the API call
    """
    def __init__(self):
        logger.debug('EXCEPTION: %s', 'PermanentException: There is an error with your api call', extra=d)
        logger.error('Error with the API call')


class CallFailException(Exception):
    """
    Raise an exception is there is an error making the API call
    """
    def __init__(self):
        logger.debug('EXCEPTION: %s', 'CallFailException: There seems to be an error with your API call', extra=d)
        logger.warning('API call failed...')
