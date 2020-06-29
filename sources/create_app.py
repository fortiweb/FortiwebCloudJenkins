
import argparse
import sys
from api.app import create_app
from api.cloudwaf import SendHandler

def getOptions(args=sys.argv[1:]):
    print(args)
    parser = argparse.ArgumentParser(description="Parses Command.")
    parser.add_argument("-u", "--username", help="User Name.")
    parser.add_argument("-p", "--password", help="password.")
    parser.add_argument("-d", "--domain", help="Domain Name.")
    parser.add_argument("-s", "--server", help="Server IP")
    parser.add_argument("-a", "--app", help="APP Name")
    parser.add_argument("-t", "--http", type=int, default=80, help="HTTP Port")
    parser.add_argument("-P", "--https", type=int, default=443, help="HTTPS Port")
    parser.add_argument("-g", "--cdn", default="False", help="Global CDN Status")
    parser.add_argument("-b", "--block", default="False", help="Block Status")
    parser.add_argument("-T", "--Template", default="", help="Template Name")

    parser.add_argument("-e", "--extra", default="", help="Extra domain names")
    parser.add_argument("-S", "--service", default="HTTPS", help="Server support service")
    parser.add_argument("-D", "--port", default="443", help="Origin server port")

    options = parser.parse_args(args)
    data = dict({})

    data["domain"] = options.domain
    data["server"] = options.server
    data["app_name"] = options.app
    extra = []
    if options.extra != "":
        extra_domains = options.extra.split("\n")
        for e in extra_domains:
            if e.strip() != "":
                extra.append(e.strip())

    data["extra_domains"] = extra
    data["app_service"] = {"http": options.http, "https": options.https}

    data["backend_type"] = options.service  # origin_server_service
    data["port"] = options.port  # "origin_server_port"
    cdn = str(options.cdn)
    if cdn.lower() == "false":
        data["cdn"] = False
    else:
        data["cdn"] = True

    block = str(options.block)
    if block.lower() == "false":
        data["block"] = 0
    else:
        data["block"] = 1

    data["template"] = options.Template

    data["http"] = options.http
    data["https"] = options.https

    handler = SendHandler(options.username, options.password)
    data["handler"] = handler
    return data

data = getOptions()
create_app(data=data)




