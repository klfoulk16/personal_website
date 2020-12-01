"""Set up all the essential flask peices and app routes. Connect database that contains the blog posts and information."""

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, LoginForm
import datetime

# Configure app
app = Flask(__name__)

"""Set up the app config"""
# Specify which environment we're using
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:secretsauce1234@localhost/personal_website'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config.update(
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'foulkelly1@gmail.com',
	MAIL_PASSWORD = '@RandomPassword',
    #MISC SETTINGS
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True
	)

db = SQLAlchemy(app)
mail = Mail(app)

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

class User(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'user'

    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

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

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = b'L@\xf1\xd6\xb0z\xb5\x8f\xc8Nj\xcat\xf9\xa7\x91'

@login_manager.user_loader
def load_user(user_id):
    """Given *user_id*, return the associated User object.

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
    post.date = post.date.strftime('%B %d, %Y')
    return render_template('post.html', post=post)

@app.route('/<category>', methods=['GET'])
def post_layout(category):
    posts = Posts.query.filter_by(category=category)
    for post in posts:
        post.date = post.date.strftime('%B %d, %Y')
    return render_template('post_layout.html', posts=posts, category=category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)

if __name__ == '__main__':
    app.run()
