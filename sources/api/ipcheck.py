
from api.request import RequestAuth

class ServerTest(RequestAuth):
    def __init__(self, token="", server="", backend_type="HTTPS", domain="www.demo.com"):
        # backend_ip=166.111.4.100&backend_type=HTTPS&domain_name=www.tsinghua.edu.cn
        if backend_type == "BOTH":
            backend_type = "HTTPS"
        query = {"backend_ip": server, "backend_type": backend_type, "domain_name": domain}
        super().__init__(path="backend-ip-test", query=query, token=token)

    def pserver_test(self):
        res = self.send()
        if res.get("head_status_code", 400) == 200:
            return True
        else:
            raise Exception("Invalid server backend!")


class IPRegion(RequestAuth):
    def __init__(self, token="", domain="www.demo.com", server="", backend_type="HTTPS", http=80, https=443):
        # {"custom_port":{"http":80,"https":443},"domain_name":"www.tsinghua.edu.cn","extra_domains":[],"ep_ip":"166.111.4.100"}
        api_data = dict({"custom_port": {}, "domain_name": domain, "extra_domains": [], "ep_ip": server})
        if backend_type == "BOTH":
            api_data["custom_port"]["http"] = http
            api_data["custom_port"]["https"] = https
        elif backend_type == "HTTPS":
            api_data["custom_port"]["https"] = https
        else:
            api_data["custom_port"]["http"] = http
        data = dict({"ep_ip": server, "domain_name": domain})
        super().__init__(path="check-ip-region", method="POST", data=data, token=token)

    def get_ip_region(self):
        res = self.send()
        loc = res.get("location")
        if loc:
            print(f"Check the pserver belong to the country/region {loc}")
            return res
        else:
            raise Exception("Invalid server backend, couldn't pserver belong any cm region!")
