from api.request import RequestBase


class Token(RequestBase):
    def __init__(self, username='admin', password='', handler=None):
        # (self, username='admin', password='', method='GET', path="", query='', data={}, timeout=3, **kargs):
        data = dict({
            "username": username,
            "password": password
        })
        super().__init__(method='POST', path='token', data=data, handler=handler)

    def get_token(self):
        data = self.send()
        return data.get("token", None)
