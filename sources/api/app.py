import json
from api.request import RequestAuth
from api.token import Token
from api.ipcheck import ServerTest, IPRegion
from api.template import Template

class AppCreate(RequestAuth):

    def __init__(self, token, data={}, region=None, template=None):
        # def __init__(self, method='GET', path="", query='', data={}, timeout=3, **kargs):

        api_data = dict({"app_name": data.get("app", "default_app_name"),
                          "domain_name": data.get("domain"),
                          "extra_domain": [],
                          "block_mode": data.get("block_mode", 0),
                          "server_address": data.get("pserver"),
                          # "custom_port": {},
                          "service": [],
                          "template_enable": 0,
                          "head_availability": 1,
                          "head_status": 200})
        if data.get("cdn"):
            api_data["cdn_status"] = 1
        else:
            api_data["cdn_status"] = 0
            api_data["server_country"] = region.get("location")
            api_data["region"] = region.get("cluster").get("single")

        if template:
            api_data["template_enable"] = 1
            api_data["template_id"] = template

        backend_type = data.get("custom")
        if backend_type == "BOTH":
            # api_data["custom_port"]["http"] = data.get("http")
            # api_data["custom_port"]["https"] = data.get("https")
            api_data["service"].append("http")
            api_data["service"].append("https")
            api_data["server_type"] = "https"

        elif backend_type == "HTTPS":
            # api_data["custom_port"]["https"] = data.get("https")
            api_data["service"].append("https")
            api_data["server_type"] = "https"

        else:
            # api_data["custom_port"]["http"] = data.get("http")
            api_data["service"].append("http")
            api_data["server_type"] = "http"

        super().__init__(method='POST', path="application", data=api_data, token=token)

    def check(self):
        pass

    def create(self):
        self.send()


class AppQuery(RequestAuth):
    def __init__(self, token, domain="", **kwargs):
        self.domain = domain
        con = dict({"size": 1, "cursor": "", "forward": True, "filter": ""})
        filter_con = dict({"id": "domain_name", "logic": {"is": {"string": True}, "search": "string"}, "value": [domain]})
        con["filter"] = json.dumps([filter_con])
        super().__init__(path="application", query=con, token=token)

    def get_ep_id(self):
        res = self.send()
        app_list = res.get("app_list", [])
        if len(app_list) > 0:
            return app_list[0]["ep_id"]
        else:
            print(f"Not exist domain id for domain name {self.domain}")
            return None


class AppDel(RequestAuth):

    def __init__(self, token, domain=""):
        query = AppQuery(token, domain=domain)
        self.ep_id = query.get_ep_id()
        self.illegal = True
        if self.ep_id:
            super().__init__(method='DELETE', path=f"application/{self.ep_id}", token=token)
            self.illegal = False
        else:
            raise Exception(f"Get an illegal domain {domain}")

    def del_it(self):
        if not self.illegal:
            self.send()
            print("Delete domain successfully")
        else:
            print("Delete domain failed")


def create_app(data={}):
    print(f"Get the data: {data}")
    token = Token(username=data.get("username", ""), password=data.get("password", ""))
    token = token.get_token()
    if token:
        template_id = None
        region = None
        template = data.get("template")
        if template.strip() != "":
            template = Template(token=token)
            template_id = template.get_id_by_name(data.get("template"))
        if not data.get("cdn"):
            tester = ServerTest(token=token, server=data.get("pserver"),
                                backend_type=data.get("custom"), domain=data.get("domain"))

            tester.pserver_test()

            region_checker = IPRegion(token=token, domain=data.get("domain"),
                                      server=data.get("pserver"), backend_type=data.get("custom"),
                                      http=data.get("http"), https=data.get("https"))
            region = region_checker.get_ip_region()
        app = AppCreate(token, data=data, region=region, template=template_id)
        app.check()
        app.create()

    else:
        raise Exception("Invalid username or password!")


def del_app(data={}):
    token = Token(username=data.get("username", ""), password=data.get("password", ""))
    token = token.get_token()
    if token:
        domain = data.get("domain", None)
        app = AppDel(token, domain=domain)
        app.del_it()
    else:
        raise Exception("Invalid username or password!")
