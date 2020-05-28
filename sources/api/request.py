import os
import json
import time
import requests
import threading
import urllib.parse


from api.settings import (API_VER, DOMAIN)

requests.packages.urllib3.disable_warnings()

# Global FWB REST connection session
_glb_sess_lock = threading.RLock()
_glb_request_sess = None


def _get_default_fwb_session():
    """
    Return a global session object shared by FWB REST API.
    """
    global _glb_request_sess

    with _glb_sess_lock:

        if _glb_request_sess is None:
            _glb_request_sess = requests.Session()

            fwb_adp = requests.adapters.HTTPAdapter(
                pool_connections=64,
                pool_maxsize=64,
                max_retries=3)

            _glb_request_sess.mount('https://', fwb_adp)
            _glb_request_sess.mount('http://', fwb_adp)

    return _glb_request_sess


class RequestBase(object):
    def __init__(self, method='GET', path="", query='', data={}, timeout=60, **kargs):
        self.method = method
        self.data = data
        self.timeout = timeout
        if type(query) == "string":
            self.query = query
        else:
            # dict
            self.query = urllib.parse.urlencode(query)

        self.api_ver = API_VER
        self.domain = DOMAIN
        self.path = path
        self.url = self._set_url()

        self.headers = dict()

        self.set_headers('Content-Type', 'application/json')
        self.set_headers('Accept', 'text/plain')

    @staticmethod
    def _format_path(path):
        return '/'.join([seg for seg in path.split('/') if len(seg)])

    def _set_url(self):
        url = requests.compat.urljoin(self.domain, self.api_ver + "/")
        url = requests.compat.urljoin(url, self.path)
        print("set url is>>")
        print(url)
        if self.query:
            query_str = self.query if self.query.startswith('?') else '?' + self.query
            url = requests.compat.urljoin(url, query_str)
        return url

    def set_headers(self, key, value):
        self.headers[key] = value

    def validate(self):
        """
        Validate the setup of rest api
        """
        if not self.method in ('GET', 'POST', 'PUT', 'DELETE'):
            raise Exception("REST API method %s not supported" % self.method)

    def get(self, data={}):
        session = _get_default_fwb_session()
        return session.get(
            url=self.url, headers=self.headers,
            verify=False, timeout=self.timeout)

    def delete(self, data={}):
        session = _get_default_fwb_session()

        return session.delete(
            url=self.url, headers=self.headers,
            verify=False, timeout=self.timeout)

    def put(self, data={}):
        session = _get_default_fwb_session()
        return session.put(
            url=self.url, headers=self.headers,
            data=json.dumps(data), verify=False,
            timeout=self.timeout)

    def post(self, data={}):
        session = _get_default_fwb_session()
        return session.post(
            url=self.url, headers=self.headers,
            data=json.dumps(data), verify=False,
            timeout=self.timeout)

    def send(self, data=None):
        """
        Send rest api, and wait its return.
        """
        self.validate()

        try:
            ts = time.time()

            method_val = getattr(self, self.method.lower(), self.get)
            d = data or self.data
            print(f"send data {d}")
            response = method_val(data=d)
            duration = time.time() - ts
            print(f"URL:{self.url}, method:{self.method} finished, duration:{duration}")

        except Exception as e:
            raise Exception("Failed to connect to %s: %s" % (self.url, e))

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


class RequestAuth(RequestBase):

    def __init__(self, method='GET', path="", query='', data={}, timeout=60, **kargs):
        super().__init__(method=method, path=path, query=query, data=data, timeout=timeout, **kargs)
        token = kargs.get("token")
        self.set_headers("Authorization", token)

