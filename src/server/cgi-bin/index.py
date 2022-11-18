
import cgi
import cgitb
import data
import scrap

cgitb.enable()

form = cgi.FieldStorage()

link = data.load()["link"]

if form.getfirst("update"):
    templateName = "template/indexUpdate.template"
else:
    templateName = "template/index.template"

template = scrap.readTemplate(templateName)

scrap.printContentType()

exec(template)
