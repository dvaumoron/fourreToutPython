
import cgi
import cgitb
import data
import scrap

cgitb.enable()

form = cgi.FieldStorage()

index = form.getfirst("index")

if index == "new":
    title = "Ajouter le lien"
    name = ""
    link = "/"
else:
    title = "Modifier le lien"
    name, link = data.load()["link"][int(index)]

template = scrap.readTemplate("template/indexField.template")

scrap.printContentType()

exec(template)
