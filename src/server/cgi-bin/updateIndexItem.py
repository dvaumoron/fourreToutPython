
import cgi
import cgitb
import data
import scrap

cgitb.enable()

form = cgi.FieldStorage()

index = form.getfirst("index")
name = form.getfirst("name")
link = form.getfirst("link")

d = data.load()

links = d["link"]

el = [name, link]

if index == "new":
    links.append(el)
    msg = "&Eacute;l&eacute;ment ajout&eacute;"
else:
    links[int(index)] = el
    msg = "&Eacute;l&eacute;ment modifi&eacute;"

data.dump(d)

template = scrap.readTemplate("template/success.template")

scrap.printContentType()

exec(template)
