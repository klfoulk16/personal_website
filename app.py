from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Configure app
app = Flask(__name__)

"""Set up the app config"""
# Specify which environment we're using
ENV = 'dev'

if ENV == 'prod':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = '***REMOVED***'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = '***REMOVED***'

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

# if you need to redo the db setup, drop the table and then run python in terminal and then these commands:
    # >>> from app import db
    # >>> db.create_all()
    # >>> exit()

"""
code I used to add myself to user db:
>>> from app import db
>>> from app import Admin
>>> admin1 = Admin("klf16@my.fsu.edu", "password")
>>> db.session.add(admin1)
>>> db.session.commit()
>>> exit()

"""

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

class PostImages(db.Model):
    __tablename__ = 'post_images'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    img_path = db.Column(db.String(175))
    header = db.Column(db.Boolean)

    def __init__(self, post_id, img_path, header):
        self.post_id = h1
        self.img_path = sample
        self.header = body

class Admin(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'admin'
    email = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

class Subscribers(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.String(50))
    last = db.Column(db.String(50))
    email = db.Column(db.String(50))
    still_subscribed = db.Column(db.Boolean, default=True)
    date_subscribed = db.Column(db.Date)
    date_unsubscribed = db.Column(db.Date)

    def __init__(self, first, last, email):
        self.first = first
        self.last = last
        self.email = email
        self.date_subscribed = datetime.date.today()

@login_manager.user_loader
def load_user(user_id):
    """
    Given *user_id*, return the associated User object.
    :param unicode user_id: user_id (email) user to retrieve

    """
    return Admin.query.get(user_id)

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
    first = request.form['first']
    last = request.form['last']
    email = request.form['email']

    data = Subscribers(first, last, email)
    db.session.add(data)
    db.session.commit()

    # have this automatically send a welcome email to confirm people.
    # maybe this should return some URL so we know that the person is subscribed?
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
        user = Admin.query.get(email)
        print(user.email, user.password_hash)
        print(request.form['password'])
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

# send email to all marinas
@app.route('/send-mail')
def send_mail():
    # get list of all marina's info
    subs = Subscribers.query.filter_by(still_subscribed=True).all()
    for sub in subs:
        msg = Message("Hi everyone",
        sender="foulkelly1@gmail.com",
        recipients=[sub.email])
        msg.body = "This is the body."
        msg.html = render_template('/test-posts/test1.html')
        mail.send(msg)
    flash('Success, the mail has been sent.')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run()
