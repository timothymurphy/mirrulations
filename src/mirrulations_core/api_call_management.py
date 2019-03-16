import logging
import requests
import time
import mirrulations_core.config as config

key = config.read_value('key')

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='api_call_management.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'CLIENT'}
logger = logging.getLogger('tcpserver')


def call(url):
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
    if 300 <= result.status_code < 400:
        logger.debug('Exception: %s', 'TemporaryException for return docs', extra=d)
        logger.warning('API call failed')
        raise TemporaryException
    if result.status_code == 429:
        logger.debug('Exception: %s', 'ApiCountZeroException for return docs', extra=d)
        logger.warning('API call failed')
        raise ApiCountZeroException
    if 400 <= result.status_code < 600:
        logger.debug('Exception: %s', 'PermanentException for return docs', extra=d)
        logger.warning('API call failed')
        raise PermanentException
    logger.warning('API call successfully made')
    return result


def add_api_key(url):
    """
    The API key will not be given in the url so it must be added
    :param url: the url that will be used to make the API call
    :return: returns the url containing the API key
    """
    return url + "&api_key=" + str(key)


def api_call_manager(url):
    """
    If there were no errors in making an API call, get the result
    If a Temporary error occurred, sleep for 5 minutes and try again. Do this 50 times, and if it continues to fail, raise a CallFailException
    If a Permanent error occurs, raise a CallFailException
    If the user's ApiCount is zero, sleep for one hour to refresh the calls
    :param url: the url that will be used to make the API call
    :return: returns the resulting information of the documents
    """

    logger.debug('Call Successful: %s', 'api_call_mangement: starting API Call Manager', extra=d)
    logger.info('Managing API call...')

    pause = 0
    while pause < 51:
        try:
            return call(url)
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
        except ApiCountZeroException:
            logger.debug('Exception: %s', 'api_call_mangement: Caught ApiCountZeroException. Waiting 1 hour.', extra=d)
            logger.error('Error: ran out of API calls')
            time.sleep(3600)
    logger.debug('Exception: %s', 'api_call_mangement: CallFailException for return docs', extra=d)
    logger.debug('Incomplete: %s', url, extra=d)
    logger.error('API call failed...')
    raise CallFailException


class TemporaryException(Exception):
    """
    Raise an exception if there is an error communicating with either the work server or regulations
    """
    def __init__(self):
        logger.debug('EXCEPTION: %s', 'TemporaryException: There seems to be a connection error', extra=d)
        logger.error('Error connecting to API')


class ApiCountZeroException(Exception):
    """
    Raise an exception if the user is out of API calls
    """
    def __init__(self):
        logger.debug('EXCEPTION: %s', 'ApiCountZeroException: You have used all of your api calls', extra=d)
        logger.error('Error - ran out of API calls')


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
