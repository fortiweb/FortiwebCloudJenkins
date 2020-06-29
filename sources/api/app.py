import json
from api.request import RequestBase

from api.ipcheck import ServerTest, IPRegion, DnsLookup, is_ip_address
from api.template import Template


class AppCreate(RequestBase):

    def __init__(self, data={}, region=None, test_result={}, template=None, handler=None):
        # def __init__(self, method='GET', path="", query='', data={}, timeout=3, **kargs):
        self.domain = data.get("domain")
        api_data = dict({"app_name": data.get("app_name", "default_app_name"),
                          "domain_name": self.domain,
                          "extra_domains": data.get("extra_domains", []),
                          "block_mode": data.get("block", 0),
                          "server_address": data.get("server"),
                          "custom_port": {},
                          "service": data.get("app_service", {}),
                          "template_enable": 0,
                          "head_availability": test_result.get("head_availability", 1),
                          "head_status_code": test_result.get("head_status_code", 200)})
        if data.get("cdn"):
            api_data["cdn_status"] = 1
        else:
            api_data["cdn_status"] = 0
            api_data["server_country"] = region.get("location")
            api_data["region"] = region.get("cluster").get("single")

        if template:
            api_data["template_enable"] = 1
            api_data["template_id"] = template

        api_data["server_type"] = data.get("backend_type", "").lower()
        service = data.get("app_service", {})
        api_data["service"] = list(service.keys())
        api_data["custom_port"] = service
        platform = region.get("region", [])
        api_data["platform"] = platform[0] if len(platform) > 0 else "AWS"
        # api_data["platform"] = "C8"

        super().__init__(method='POST', path="application", data=api_data, handler=handler)

    def check(self):
        query = AppQuery(handler=self.handler, domain=self.domain)
        if query.get_ep():
            return False
        else:
            return True

    def create(self):
        return self.send()


class AppQuery(RequestBase):
    def __init__(self, domain="", app_name="", handler=None, **kwargs):
        self.domain = domain
        self.app_name = app_name
        con = dict({"size": 1, "cursor": "", "forward": True, "filter": ""})
        url = "application"
        if domain:
            filter_con = dict(
                {"id": "domain_name", "logic": {"is": {"string": True}, "search": "string"}, "value": [domain]})
            con["filter"] = json.dumps([filter_con])
        else:
            con = dict({"partial": True})
        super().__init__(path=url, query=con, handler=handler)

    def get_ep(self):
        res = self.send()
        if isinstance(res, dict):
            app_list = res.get("app_list", [])
        elif isinstance(res, list):
            app_list = res
        else:
            app_list = []
        if len(app_list) > 0:
            for app in app_list:
                if app['app_name'] == self.app_name or app['domain_name'] == self.domain:
                    return app
            return None
        else:
            print("Not exist domain")
            return None

    def get_ep_id(self):
        ep = self.get_ep()
        if ep:
            return ep["ep_id"]
        else:
            return None


class AppDel(RequestBase):
    def __init__(self, handler=None, ep_id=""):
        self.ep_id = ep_id
        super().__init__(method='DELETE', path=f"application/{self.ep_id}", handler=handler)

    def del_it(self):
        self.send()
        print("Delete domain successfully")


class AppGet(RequestBase):
    def __init__(self, handler=None, ep_id=""):
        self.ep_id = ep_id
        super().__init__(path=f"application/{self.ep_id}/endpoint", handler=handler)

    def get_ep_data(self):
        res = self.send()
        return res

class AppUpdate(RequestBase):
    def __init__(self, data={}, handler=None, ep_id=""):
        self.ep_id = ep_id
        super().__init__(method='PUT', path=f"application/{self.ep_id}", data=data, handler=handler)

    def update_ep(self):
        res = self.send()
        return res


def create_app(data={}):
    print(f"Get the data: {data}")

    template_id = None
    region = None
    server_ips = []
    query = AppQuery(app_name=data.get("app_name"), handler=data.get("handler", None))
    ep = query.get_ep()
    if ep:
        return ep, False

    template = data.get("template")
    if template.strip() != "":
        template = Template(handler=data.get("handler", None))
        template_id = template.get_id_by_name(data.get("template"))

    if not is_ip_address(data.get("server")):
        dns = DnsLookup(data.get("server"), handler=data.get("handler"))
        server_ips = dns.get_server_address()
        tester = ServerTest(server=server_ips,
                            backend_type=data.get("backend_type"), domain=data.get("domain"),
                            handler=data.get("handler", None))
    else:
        tester = ServerTest(server=data.get("server"),
                            backend_type=data.get("backend_type"), domain=data.get("domain"),
                            handler=data.get("handler", None))
    test_res = tester.pserver_test()

    region_checker = IPRegion(domain=data.get("domain"),
                              server=server_ips or data.get("server"), extra_domains=data.get("extra_domains"),
                              service=data.get("app_service"),
                              handler=data.get("handler", None))
    region = region_checker.get_ip_region()
    app = AppCreate(data=data, region=region, test_result=test_res, template=template_id,
                    handler=data.get("handler", None))
    if not app.check():  # exist app
        return {}, False
    else:
        return app.create(), True


def del_app(data={}):
    app_name = data.get("app_name", None)
    query = AppQuery(app_name=app_name, handler=data.get("handler", None))
    ep_id = query.get_ep_id()
    if ep_id:
        app = AppDel(handler=data.get("handler", None), ep_id=ep_id)
        app.del_it()

