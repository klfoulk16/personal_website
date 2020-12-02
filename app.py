"""Set up all the essential flask peices and app routes. Connect database that contains the blog posts and information."""

from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime
from models import *

# Configure app
app = Flask(__name__)

"""Set up the app config"""
# Specify which environment we're using
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = '***REMOVED***'
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
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True
	)

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
app.secret_key = ***REMOVED***

@login_manager.user_loader
def load_user(user_id):
    """
    Given *user_id*, return the associated User object.
    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


"""
App Routes
"""

@app.route('/')
def index():
    posts = Posts.query.order_by(Posts.id.desc()).all()
    for post in posts:
        post.date = post.date.strftime('%B %d, %Y')
    return render_template('index.html', posts=posts)

@app.route('/post/<id>', methods=['GET'])
def view_post(id):
    post = Posts.query.filter_by(id=id).first()
    post.date = post.date.strftime('%B %d, %Y')
    return render_template('post.html', post=post)

@app.route('/<category>', methods=['GET'])
def post_layout(category):
    posts = Posts.query.filter_by(category=category).order_by(Posts.id.desc()).all()
    for post in posts:
        post.date = post.date.strftime('%B %d, %Y')
    return render_template('post_layout.html', posts=posts, category=category)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    return ('', 204)

"""
Handling the admin user (aka me).
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    if request.method == "POST":
        email = request.form['email']
        user = User.query.get(email)
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            flash('What would you like to do today?')
            return redirect(url_for('admin'))
        return render_template('login.html', message="Username or password incorrect.")
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == "POST":
        h1 = request.form['h1']
        sample = request.form['sample']
        body = request.form['body']
        category = request.form['category']

        data = Posts(h1, sample, body, category)
        db.session.add(data)
        db.session.commit()
        flash('Success, your post is live.')
        return redirect(url_for('admin'))

    else:
        return render_template('create.html')

@app.route('/admin', methods=['GET'])
@login_required
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run()


"""
code I used to add myself to user db:
>>> from app import db
>>> from app import User
>>> user = User("klf16@my.fsu.edu", "password")
>>> db.session.add(user)
>>> db.session.commit()
>>> exit()

"""
