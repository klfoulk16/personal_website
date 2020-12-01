from flask_sqlalchemy import SQLAlchemy

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
