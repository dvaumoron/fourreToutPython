
import cgi
import cgitb
import scrap

cgitb.enable()

form = cgi.FieldStorage()

name = form.getfirst("name", "world")

template = scrap.readTemplate("template/hello.template")

scrap.printContentType()

exec(template)
