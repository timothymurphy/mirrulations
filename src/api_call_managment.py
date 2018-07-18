import time

from api_call import *



def api_call_manager(url):
    """
    If there were no errors in making an api call, get the result
    If a Temporary error occurred, sleep for 5 minutes and try again. Do this 50 times, and if it continues to fail, raise a CallFailException
    If a Permanent error occurs, raise a CallFailException
    If the users ApiCount is zero, sleep for one hour to refresh the calls
    :param url: the url that will be used to make the api call
    :return: returns the resulting information of the documents
    """
    pause = 0
    while pause < 51:
        try:
            result = call(url)
            return result
        except TemporaryException:
            time.sleep(300)
            pause += 1
        except PermanentException:
            break
        except ApiCountZeroException:
            time.sleep(3600)
    raise CallFailException


# Raise an exception is there is an error making the api call
class CallFailException(Exception):
    print("NOTICE: There is an error with your API call")
