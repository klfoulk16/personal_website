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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:secretsauce1234@localhost/personal_website'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.update(
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'foulkelly1@gmail.com',
	MAIL_PASSWORD = '@RandomPassword',
    #MISC SETTINGS
    SQLALCHEMY_TRACK_MODIFICATIONS = False
	)

mail = Mail(app)
db = SQLAlchemy(app)

# if you need to redo the db setup, drop the table and then run python in terminal and then these commands:
    # >>> from app import db
    # >>> db.create_all()
    # >>> exit()

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    h1 = db.Column(db.String(100))
    sample = db.Column(db.String(175))
    body = db.Column(db.Text())
    category = db.Column(db.String(200))
    date = db.Column(db.Date())

    def __init__(self, h1, sample, body, category):
        self.h1 = h1
        self.sample = sample
        self.body = body
        self.category = category
        self.date = datetime.date.today()

@app.route('/')
def index():
    posts = Posts.query.all()
    for post in posts:
        post.date = post.date.strftime('%B %d, %Y')
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == "POST":
        h1 = request.form['h1']
        sample = request.form['sample']
        body = request.form['body']
        category = request.form['category']

        data = Posts(h1, sample, body, category)
        db.session.add(data)
        db.session.commit()
        return render_template('create.html', success=True)

    else:
        return render_template('create.html', success=False)

@app.route('/post/<id>', methods=['GET'])
def edit(id):
    post = Posts.query.filter_by(id=id).first()
    return render_template('post.html', post=post)

if __name__ == '__main__':
    app.run()
