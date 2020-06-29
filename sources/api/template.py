from api.request import RequestBase


class Template(RequestBase):

    def __init__(self,  handler=None):
        # def __init__(self, method='GET', path="", query='', data={}, timeout=3, **kargs):
        super().__init__(path="template", handler=handler)

    def get_id_by_name(self, name):
        templates = self.send()
        if name.strip() != "":
            tlist = templates.get("result", [])
            for t in tlist:
                if t["name"] == name:
                    return t["template_id"]
            raise Exception("Invalid template name!")
        return ""

