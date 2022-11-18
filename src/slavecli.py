
import argparse
import xmlrpc.client

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", action="version",
                    version="%(prog)s version 0.3")
parser.add_argument("host")
parser.add_argument("action", choices=["start", "cancel", "monitor"])

args = parser.parse_args()

with xmlrpc.client.ServerProxy(args.host) as server:
    print(getattr(server, args.action)())
