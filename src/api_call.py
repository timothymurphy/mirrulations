import requests
import os

home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()


def call(url):

    """
    Sends an api call to regulations.gov
    Raises exceptions if it is not a valid api call
    When a 300 status code is given, return a temporary exception so the user can retry the api call
    When a 429 status code is given, the user is out of api calls and must wait an hour to make more
    When 400 or 500 status codes are given there is a problem with the api connection
    :param url: the url that will be used to make the api call
    :return: returns the json format information of the documents
    """
    result = requests.get(url)
    if 300 <= result.status_code < 400:
        raise TemporaryException
    if result.status_code == 429:
        raise ApiCountZeroException
    if 400 <= result.status_code < 600:
        raise PermanentException
    return result


# The api key will not be given in the url so it must be added
def add_api_key(url):
    return url + "&api_key=" + str(key)


# Raise an exception if there is an error communicating
class TemporaryException(Exception):
    print("NOTICE: There seems to be a connection error")


# Raise an exception if the user is out of api calls
class ApiCountZeroException(Exception):
    print("NOTICE: You have used all your API calls.")


# Raise an exception if there is an error with the API call
class PermanentException(Exception):
    print("NOTICE: There is an error with your API call")