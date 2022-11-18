
import cgi
import cgitb
import data
import scrap

cgitb.enable()

form = cgi.FieldStorage()

index = int(form.getfirst("index"))

d = data.load()

links = d["link"]

if form.getfirst("up"):
    index2 = index + 1
else:
    index2 = index - 1

links[index], links[index2] = links[index2], links[index]

data.dump(d)

msg = "&Eacute;l&eacute;ment deplac&eacute;"

template = scrap.readTemplate("template/success.template")

scrap.printContentType()

exec(template)
