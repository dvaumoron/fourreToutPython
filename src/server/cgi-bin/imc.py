
import cgi
import cgitb
import scrap

cgitb.enable()

form = cgi.FieldStorage()

poids = form.getfirst("poids")
taille = form.getfirst("taille")

if poids is None or taille is None:
    errorMsg = "Vous devez renseigner le poids et la taille"
    templateName = "template/error.template"
else:
    try:
        imc = round(float(poids) / (float(taille) ** 2), 2)

        if imc < 20:
            categorie = "maigre"
        elif imc < 25:
            categorie = "normal"
        elif imc < 30:
            categorie = "en surpoids"
        else:
            categorie = "obèse"
    
        templateName = "template/imc.template"
    except ValueError:
        errorMsg = "Le poids et la taille doivent être des nombres"
        templateName = "template/error.template"

template = scrap.readTemplate(templateName)

scrap.printContentType()

exec(template)
