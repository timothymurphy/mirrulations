import time
import logging
from api_call import *


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='api_call_management.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'CLIENT'}
logger = logging.getLogger('tcpserver')

def api_call_manager(url):
    """
    If there were no errors in making an api call, get the result
    If a Temporary error occurred, sleep for 5 minutes and try again. Do this 50 times, and if it continues to fail, raise a CallFailException
    If a Permanent error occurs, raise a CallFailException
    If the user's ApiCount is zero, sleep for one hour to refresh the calls
    :param url: the url that will be used to make the api call
    :return: returns the resulting information of the documents
    """

    logger.warning('Call Successful: %s', 'api_call_mangement: starting API Call Manager', extra=d)

    pause = 0
    while pause < 51:
        try:
            result = call(url)
            return result
        except TemporaryException:
            logger.warning('Exception: %s', 'api_call_mangement: Caught TemporaryException, waiting 5 minutes. Current pause: ' + pause, extra=d)
            time.sleep(300)
            pause += 1
        except PermanentException:
            logger.warning('Exception: %s', 'api_call_mangement: Caught PermanentException', extra=d)
            break
        except ApiCountZeroException:
            logger.warning('Exception: %s', 'api_call_mangement: Caught ApiCountZeroException. Waiting 1 hour.', extra=d)
            time.sleep(3600)
    logger.warning('Exception: %s', 'api_call_mangement: CallFailException for return docs', extra=d)
    raise CallFailException


# Raise an exception is there is an error making the api call
class CallFailException(Exception):
    print("NOTICE: There is an error with your API call")
