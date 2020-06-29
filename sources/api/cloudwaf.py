import json
import requests
import threading
from api.settings import DOMAIN

requests.packages.urllib3.disable_warnings()

# Global FWB REST connection session
_glb_sess_lock = threading.RLock()
_glb_request_sess = None

class SendHandler(object):
    def __init__(self, username, password):
        self.handle = self._create_session_handler()
        self.domain = DOMAIN
        self.timeout = 60
        self.token = ""
        self.connected = False
        self.username = username
        self.password = password
        self.headers = {}

    @staticmethod
    def _create_session_handler():
        """
        Return a global session object shared by FWB REST API.
        """
        global _glb_request_sess

        with _glb_sess_lock:

            if _glb_request_sess is None:
                _glb_request_sess = requests.Session()

                cloud_adp = requests.adapters.HTTPAdapter(
                    pool_connections=64,
                    pool_maxsize=64,
                    max_retries=3)

                _glb_request_sess.mount('https://', cloud_adp)
                _glb_request_sess.mount('http://', cloud_adp)

        return _glb_request_sess

    def set_auth_header(self):
        self.set_headers('Content-Type', 'application/json')
        self.set_headers('Accept', 'text/plain')
        self.set_headers('Authorization', self.token)
        return self.headers

    def set_headers(self, key, value):
        self.headers[key] = value

    def get(self, url, **kargs):
        return self.handle.get(
            url=url, headers=kargs.get("headers", {}),
            verify=False, timeout=self.timeout)

    def delete(self, url, **kargs):

        return self.handle.delete(
            url=url, headers=kargs.get("headers", {}),
            verify=False, timeout=self.timeout)

    def put(self, url, **kargs):
        return self.handle.put(
            url=url, headers=kargs.get("headers", {}),
            data=kargs.get("data", ""), verify=False,
            timeout=self.timeout)

    def post(self, url, **kargs):

        return self.handle.post(
            url=url, headers=kargs.get("headers", {}),
            data=kargs.get("data", ""), verify=False,
            timeout=self.timeout)

    def login(self):
        data = dict({
            "username": self.username,
            "password": self.password
        })

        url_path = self.make_url("/v1/token")

        res = self.post(url_path, data=json.dumps(data))
        response = res.json()
        print(f"get login request {url_path} response {response}")
        token = response.get("token", None)
        if token:
            self.token = token
            self.connected = True
        else:
            raise Exception("Invalid username or password")

    def make_url(self, path):
        return self.domain + path

    def send_req(self, url, **kargs):
        """
        Send rest api, and wait its return.
        """

        try:
            if not self.connected:
                self.login()
                self.set_auth_header()

            kargs["headers"] = self.headers

            url_path = self.make_url(url)
            method = kargs.get("method", "GET")
            method_val = getattr(self, method.lower(), self.get)
            response = method_val(url_path, **kargs)
            return response
        except Exception as e:
            raise Exception("Failed to connect to %s: %s" % (url, e))

