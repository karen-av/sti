from wsgiref.validate import validator
from flask_wtf import FlaskForm
from flask_wtf import RecaptchaField
from wtforms import StringField
from wtforms.validators import DataRequired

class ContactForm(FlaskForm):
    text = StringField('Комментарий', validators = [DataRequired()])
    recaptcha = RecaptchaField()

class ContactRecaptchaForm(ContactForm):
    recaptcha = RecaptchaField()