""" Handle account endpoints"""
from apirequest import APIRequest
from decorators import endpoint
from abc import abstractmethod

class Auth(APIRequest):
    """Auth - class to handle auth endpoints"""

    ENDPOINT = ""
    METHOD = "GET"

    @abstractmethod
    def __init__(self):
        endpoint = self.ENDPOINT.format()
        super(Auth, self).__init__(endpoint, method=self.METHOD)

@endpoint('auth/refresh/')
class APIKEY(Auth):
    """AccountBalance - class to handle the account balance endpoints"""
    def __init__(self):
        super(APIKEY, self).__init__()