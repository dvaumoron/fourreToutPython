
import json
import subprocess
import xmlrpc.server

class FalsePopen():
    __slots__ = ()
    def poll(self):
        return 0

p = FalsePopen()

with open("slave.json") as f:
    d = json.load(f)
    cmd = d["cmd"]
    port = d["port"]
    del d
del f

Popen = subprocess.Popen

def start():
    global p
    if p.poll() is None:
        return "already started"
    else:
        p = Popen(cmd)
        return "started"

def cancel():
    if p.poll() is None:
        p.terminate()
        return "cancelled"
    else:
        return "not running"   

def monitor():
    if p.poll() is None:
        return "running"
    else:
        return "available"

if __name__ == "__main__":
    with xmlrpc.server.SimpleXMLRPCServer(("localhost", port)) as server:
        server.register_function(start)
        server.register_function(cancel)
        server.register_function(monitor)

        print("Listening on port", port)
        server.serve_forever()
