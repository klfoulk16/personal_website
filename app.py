"""Set up all the essential flask peices and app routes. Connect database that
contains the blog posts and information."""

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import datetime

# Configure app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Specify which environment we're using
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:PASSWORD@localhost/personal_website'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config.update(
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'foulkelly1@gmail.com',
	MAIL_PASSWORD = '***REMOVED***',
    #MISC SETTINGS
    SQLALCHEMY_TRACK_MODIFICATIONS = False
	)

mail = Mail(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# if you need to redo the db setup, drop the table and then run python in terminal and then these commands:
    # >>> from app import db
    # >>> db.create_all()
    # >>> exit()

class posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text())
    date = db.Column(db.Date())

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.date = datetime.date.today()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
