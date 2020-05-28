from api.request import RequestAuth


class Template(RequestAuth):

    def __init__(self, token=""):
        # def __init__(self, method='GET', path="", query='', data={}, timeout=3, **kargs):
        super().__init__(path="template", token=token)

    def get_id_by_name(self, name):
        templates = self.send()
        if name.strip() != "":
            tlist = templates.get("result", [])
            for t in tlist:
                if t["name"] == name:
                    return t["template_id"]
            raise Exception("Invalid template name!")
        return ""
