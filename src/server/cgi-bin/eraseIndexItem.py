
import cgi
import cgitb
import data
import scrap

cgitb.enable()

form = cgi.FieldStorage()

index = int(form.getfirst("index"))

d = data.load()

links = d["link"]
del links[index]

data.dump(d)

msg = "&Eacute;l&eacute;ment supprim&eacute;"

template = scrap.readTemplate("template/success.template")

scrap.printContentType()

exec(template)
