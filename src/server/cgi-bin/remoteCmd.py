
import cgi
import cgitb
import data
import scrap
import xmlrpc.client

cgitb.enable()

form = cgi.FieldStorage()

slave = data.load()["slave"]

action = form.getfirst("action")
index = form.getfirst("index")
if index is not None:
    index = int(index)

ServerProxy = xmlrpc.client.ServerProxy

res = []
for i, el in enumerate(slave):
    try:
        with ServerProxy(el[1]) as server:
            if i == index:
                res.append(getattr(server, action)())
            else:
                res.append(server.monitor())
    except ConnectionRefusedError:
        res.append("offline")

template = scrap.readTemplate("template/comand.template")

scrap.printContentType()

exec(template)
