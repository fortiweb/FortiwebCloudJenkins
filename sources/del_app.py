import sys
import argparse
from api.app import del_app
from api.cloudwaf import SendHandler

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parses Command.")
    parser.add_argument("-u", "--username", help="User Name.")
    parser.add_argument("-p", "--password", help="password.")
    parser.add_argument("-a", "--app", help="Domain Name.")
    options = parser.parse_args(sys.argv[1:])
    data = dict({})
    data["username"] = options.username
    data["password"] = options.password
    data["app_name"] = options.app
    handler = SendHandler(options.username, options.password)
    data["handler"] = handler
    del_app(data=data)



