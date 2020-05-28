
import argparse
import sys
from api.app import create_app

def getOptions(args=sys.argv[1:]):
    print(args)
    parser = argparse.ArgumentParser(description="Parses Command.")
    parser.add_argument("-u", "--username", help="User Name.")
    parser.add_argument("-p", "--password", help="password.")
    parser.add_argument("-d", "--domain", help="Domain Name.")
    parser.add_argument("-s", "--server", help="Server IP")
    parser.add_argument("-a", "--app", help="APP Name")
    parser.add_argument("-c", "--custom", default="HTTP", help="Custom Port")
    parser.add_argument("-t", "--trans", type=int, default=80, help="HTTP Port")
    parser.add_argument("-P", "--Port", type=int, default=443, help="HTTPS Port")
    parser.add_argument("-g", "--globals", default=False, help="Global CDN Status")
    parser.add_argument("-b", "--block", default=False, help="Block Status")
    parser.add_argument("-T", "--Template", default="", help="Template Name")
    options = parser.parse_args(args)
    data = dict({})
    data["username"] = options.username
    data["password"] = options.password
    data["domain"] = options.domain
    data["pserver"] = options.server
    data["app"] = options.app
    data["custom"] = options.custom
    data["http"] = options.trans
    data["https"] = options.Port
    data["cdn"] = options.globals
    data["block"] = options.block
    data["template"] = options.Template
    return data

data = getOptions()
create_app(data=data)




