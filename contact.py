# Contact page
from flask import (Blueprint, render_template, abort, request, flash)
from wtforms import Form, TextField, TextAreaField, BooleanField
from formencode.variabledecode import variable_encode
import smtplib
from email.MIMEText import MIMEText

# Local Project
import validation

contact_page = Blueprint('contact_page', __name__, template_folder="templates",
                         static_folder='static')

MAIL_HOST="localhost"
MAIL_PORT=25
MAIL_RECIPIENT="info@myhost.com"
MAIL_SUBJECT_PREPEND="[Flask Contact Form] "

class ContactForm(Form):
    name = TextField("Name: ")
    email = TextField("Email: ")
    phone = TextField("Phone: ")
    subject = TextField("Subject: ")
    message = TextAreaField("Message: ")
    antispam = BooleanField("I certify that this is not SPAM.")

def send_email(dataDict, responseHeaders):
    # Append dataDict key/value pairs.
    bodyStr = ""
    bodyStr += "Name: %s\n" % dataDict["name"]
    bodyStr += "Email: %s\n" % dataDict["email"]
    bodyStr += "Phone: %s\n" % dataDict["phone"]
    bodyStr += "Message: \n %s" % dataDict["message"]

    # Dump raw HTTP headers to the bottom of the e-mail
    # Useful for understanding the origination of the message
    bodyStr += "\n\n\n"
    for k,v in responseHeaders:
        bodyStr += k.upper() + ": " + v + "\n"

    email = MIMEText(bodyStr)
    email['Subject'] = MAIL_SUBJECT_PREPEND + dataDict["subject"]
    email['From'] = dataDict["email"]
    email['To'] = MAIL_RECIPIENT

    message = email.as_string()

    server = smtplib.SMTP(MAIL_HOST,MAIL_PORT)
    server.sendmail(dataDict["email"], MAIL_RECIPIENT, message)
    server.close()

    try:
        response = "thanks"
    except SMTPException:
        response = "error"
    return response


@contact_page.route('/', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == "POST":
        # There are three differente responses: thanks, invalid, and error
        response = "thanks"

        # Use variable_encode to get form entries to a normal dict.
        dataDict = variable_encode(request.form)
        responseHeaders = request.headers

        # We use this checkbox state as an inverse state of spam
        # If this is checked, we assume a bot ignored the markup and 
        # clicked it.
        # We then ignore the message, but present a false sense of 
        # success.
        antispam = True if dataDict.has_key("antispam") else False

        # If "AJAX" variable was passed via POST, this was an ajax request.
        isAjax = "AJAX" in dataDict.keys()

        # Get all invalid field entries.
        invalid = validation.invalid_fields(dataDict)

        # If we have any invalid entries at on, we respond with an invalid 
        # indicator. Otherwise, attempt to send the email.
        if invalid:
            response = "invalid"
        elif antispam:
            response == 'thanks'
        else:
            response = send_email(dataDict, responseHeaders)

        # Just return the response if this is AJAX: Do something with the response
        # with JavaScript instead of rendering the template.
        if isAjax:
            return response
        else:
            # Get information based on the response.
            info = render_template("%s.html"%response, invalid=invalid,
                                   page_title="Contact Us")

        # If the response was thanks, clear the form.
        if response == 'thanks' :
            form = ContactForm()

        return render_template("contact_t.html", form=form, info=info, page_title="Contact Us")
    else:
        return render_template("contact_t.html", form=form, page_title="Contact Us")
