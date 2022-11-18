
import cgi
import cgitb
import scrap

cgitb.enable()

form = cgi.FieldStorage()

l = form.getlist("l")

template = scrap.readTemplate("template/list.template")

scrap.printContentType()

exec(template)
