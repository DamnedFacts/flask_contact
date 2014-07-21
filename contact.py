"""
File: contact.py
Project: flask-contact (https://github.com/DamnedFacts/flask-contact)

Copyright (c) 2013, Richard Emile Sarkis <rich@sarkis.info>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Contact page
from flask import (Blueprint, render_template, request)
from wtforms import Form, TextField, TextAreaField, BooleanField, \
    SelectField, HiddenField
from formencode.variabledecode import variable_encode
import smtplib
from email.MIMEText import MIMEText

# Local Project
import validation

# import our configuration preferences for the contact form.
try:
    from config import MAIL_HOST, MAIL_PORT, MAIL_RECIPIENT, \
        MAIL_SUBJECT_PREPEND
    testing = False
except ImportError:
    print "Warning: using sample config module (config_sample)!"
    from config import MAIL_HOST, MAIL_PORT, MAIL_RECIPIENT, \
        MAIL_SUBJECT_PREPEND
    testing = True

contact_page = Blueprint('contact_page', __name__, template_folder="templates",
                         static_folder='static')

"""
The WTForms contact form. Of note:
    * The "recipient" field which may be overridden in the class before
      instantiation (and later restored).
    * The "antispam" field, which places an invisible checkbox in the form that
      form bots will see, but real users will not. This will prevent automated
      spam.
"""


class ContactForm(Form):
    choices = [(k, MAIL_RECIPIENT[k][0])
               for k in sorted(MAIL_RECIPIENT, key=MAIL_RECIPIENT.get)]
    recipient = SelectField("Send To: ", choices=choices)

    name = TextField("Name: ")
    email = TextField("Email: ")
    phone = TextField("Phone: ")
    subject = TextField("Subject: ")
    message = TextAreaField("Message: ")
    antispam = BooleanField("I certify that this is not SPAM.")

"""
Sends mail upon posting the form.
"""


def send_email(dataDict, responseHeaders):
    recipient = dataDict["recipient"]
    recipient = "{0} <{1}>".format(MAIL_RECIPIENT[recipient][0],
                                   MAIL_RECIPIENT[recipient][1])

    # Append dataDict key/value pairs.
    bodyStr = ""
    bodyStr += "Name: %s\n" % dataDict["name"]
    bodyStr += "Email: %s\n" % dataDict["email"]
    bodyStr += "Phone: %s\n" % dataDict["phone"]
    bodyStr += "Message: \n %s" % dataDict["message"]

    # Dump raw HTTP headers to the bottom of the e-mail
    # Useful for understanding the origination of the message
    bodyStr += "\n\n\n"
    for k, v in responseHeaders:
        bodyStr += k.upper() + ": " + v + "\n"

    email = MIMEText(bodyStr)
    email['Subject'] = MAIL_SUBJECT_PREPEND + dataDict["subject"]
    email['From'] = dataDict["email"]
    email['To'] = recipient

    message = email.as_string()

    server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    server.sendmail(dataDict["email"], recipient, message)
    server.close()

    try:
        response = "thanks"
    except smtplib.SMTPException:
        response = "error"
    return response

"""
Flask route for producing the contact form view.
"""


@contact_page.route('/', methods=['GET', 'POST'])
@contact_page.route('/<recipient>', methods=['GET', 'POST'])
def contact(recipient=None):
    info = None
    recip_id = recipient or request.args.get('recipient')

    # Copy our form class through inheritance
    # since WTForms performs form changes through class variable
    # modifications
    class ModContactForm(ContactForm):
        pass

    if recip_id in MAIL_RECIPIENT:
        recip_name = MAIL_RECIPIENT[recip_id][0]
        ModContactForm.recipient = HiddenField(default=recip_id)
        ModContactForm.recipientName = TextField("Send To: ",
                                                 default=recip_name)
    else:
        recip_id = None

    form = ModContactForm(request.form)

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
        antispam = True if "antispam" in dataDict else False

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

        # Just return the response if this is AJAX: Do something with the
        # response with JavaScript instead of rendering the template.
        if isAjax:
            return response
        else:
            # Get information based on the response.
            info = render_template("%s.html" % response, invalid=invalid,
                                   page_title="Contact Us")

        # If the response was thanks, clear the form.
        if response == 'thanks':
            form = ModContactForm()
    return render_template("contact_t.html", form=form, info=info,
                           selected_recipient=recip_id, testing=testing,
                           page_title="Contact Us")
