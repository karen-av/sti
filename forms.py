from wsgiref.validate import validator
from flask_wtf import FlaskForm
from flask_wtf import RecaptchaField
from wtforms import TextAreaField
from wtforms.validators import DataRequired

class ContactForm(FlaskForm):
    text = TextAreaField('Комментарий', validators = [DataRequired()])
    recaptcha = RecaptchaField()
