from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)


app.config['DEBAG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'sti.partners2@gmail.com'
app.config['MAIL_PASSWORD'] = 'feEG9e43=r4'
app.config['MAIL_DEFAULT_SENDER'] = 'sti.partners2@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)

#mail = Mail()
#mail.init_app(app)

@app.route('/')
def index():
    msg = Message('Hey There', recipients=['mahiho1080@yasiok.com'])
    mail.send(msg)
    return 'Messege hes bin sent!'

if __name__ == '__main__':
    app.run()