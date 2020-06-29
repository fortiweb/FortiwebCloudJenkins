import os
import json
import time
from api.settings import (API_VER, DOMAIN)
import urllib.parse


class RequestBase(object):
    def __init__(self, method='GET', path="", query='', data={}, handler=None, timeout=60, **kargs):
        self.method = method
        self.data = data
        self.timeout = timeout

        if type(query) == "string":
            self.query = query
        else:
            # dict
            self.query = urllib.parse.urlencode(query)

        self.api_ver = API_VER

        self.path = path
        self.url = self._set_url()

        self.headers = dict()

        self.set_headers('Content-Type', 'application/json')
        self.set_headers('Accept', 'text/plain')
        self.handler = handler

    @staticmethod
    def _format_path(path):
        return '/'.join([seg for seg in path.split('/') if len(seg)])

    def _set_url(self):
        ulist = []
        ulist.append(self.api_ver)
        ulist.append(self.path)
        url = "/".join(ulist)
        if self.query:
            query_str = self.query if self.query.startswith('?') else '?' + self.query
            url = url + query_str
        return "/" + url

    def set_headers(self, key, value):
        self.headers[key] = value

    def validate(self):
        """
        Validate the setup of rest api
        """
        if not self.method in ('GET', 'POST', 'PUT', 'DELETE'):
            raise Exception("REST API method %s not supported" % self.method)

    def send(self, data=None):
        """
        Send rest api, and wait its return.
        """
        self.validate()

        try:
            ts = time.time()

            # method_val = getattr(self, self.method.lower(), self.get)
            d = data or self.data
            print(f"send method: {self.method}, url:{self.url}, headers:{self.headers} data {d}")
            response = self.handler.send_req(
                self.url, headers=self.headers,
                data=json.dumps(d), method=self.method)

            # res = method_val(data=d)
            if not response.ok:
                if response.content:
                    print(f"get response fail result>>{response.json()}")
                    return response.json()
                else:
                    raise Exception("Failed to send REST API to %s: [%s] %s" % \
                                    (self.url, response.status_code, response.reason))

        # Return a json dict if possible,
        # otherwise return the raw content.
            try:
                print(f"get response result>>{response.json()}")
                return response.json()
            except:
                print(f"get response err result>>{response.content}")
                return response.content
        except Exception as e:
            raise Exception("Failed to connect to %s: %s" % (self.url, e))
