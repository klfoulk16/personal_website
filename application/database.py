import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Posts(db.Model):
    """
    Stores blog post information.
    """

    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    h1 = db.Column(db.String(100))
    header_path = db.Column(db.String(175))
    youtube_vid = db.Column(db.String(100))
    sample = db.Column(db.String(355))
    body = db.Column(db.Text())
    category = db.Column(db.String(200))
    date = db.Column(db.Date())

    def __init__(self, h1, sample, header_path, youtube_vid, body, category):
        self.h1 = h1
        self.sample = sample
        self.header_path = header_path
        self.youtube_vid = youtube_vid
        self.body = body
        self.category = category
        self.date = datetime.date.today()


class BodyImages(db.Model):
    """
    Stores the file locations of the images used in the body of the blog posts.
    """

    __tablename__ = "body_images"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    img_path = db.Column(db.String(175))

    def __init__(self, post_id, img_path):
        self.post_id = post_id
        self.img_path = img_path


class Subscribers(db.Model):
    """
    These are the emails and names of people who have subscribed to the website.
    """

    __tablename__ = "subscribers"
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.String(50))
    last = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    still_subscribed = db.Column(db.Boolean, default=True)
    date_subscribed = db.Column(db.Date)
    date_unsubscribed = db.Column(db.Date)

    def __init__(self, first, last, email):
        self.first = first
        self.last = last
        self.email = email
        self.date_subscribed = datetime.date.today()


class Admin(db.Model):
    """
    Database containing email and encrypted password for admin users. These users
    can create posts, edit posts, delete posts, send emails, etc.

    """

    __tablename__ = "admin"
    email = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String)
    authenticated = db.Column(db.Boolean)

    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash
        self.authenticated = False

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