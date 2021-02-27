from flask import (
    Flask,
    flash,
    render_template,
    request,
    redirect,
    url_for,
    Markup,
    Response
)
from flask_mail import Mail, Message
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import os
from dotenv import load_dotenv
from application.database import db, Admin, Posts, Subscribers, BodyImages
from application.admin import mail, login_manager

"""
App Configuration
"""

# Load environment variables
load_dotenv()

def create_app(test_config=None):

    app = Flask(__name__)

    # default configuration
    app.config.from_mapping(
        # DATABASE
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL"),
        SECRET_KEY=os.getenv("SECRET_KEY"),
        # ENV
        FLASK_ENV=os.getenv("FLASK_ENV"),
        # EMAIL SETTINGS
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=os.getenv("MAIL_PORT"),
        MAIL_USE_SSL=True,
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_USE_TLS=False,
        # MISC SETTINGS
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # ensure user doesn't upload more than 1MB of files
        MAX_CONTENT_LENGTH=1024 * 1024
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    # Make sure site isn't cached if in dev mode. Get rid of this awful crap.
    ENV = "dev"
    if ENV == "dev":
        @app.after_request
        def after_request(response):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    # Register Blueprints

    from . import admin
    app.register_blueprint(admin.bp)

    @app.route("/", methods=["GET"])
    def index():
        """
        Renders the main home page of the blog - including a short display of all posts.
        """
        posts = Posts.query.order_by(Posts.id.desc()).all()
        for post in posts:
            post.date = post.date.strftime("%B %d, %Y")
            post.header = BodyImages.query.filter_by(post_id=post.id).first()
        return render_template("index.html", posts=posts)


    @app.route("/post/<id>", methods=["GET"])
    def view_post(id):
        """
        Renders the post with a given id (the id of the post to render is passed with the route).
        """
        current_post = Posts.query.filter_by(id=id).first()

        imgs = BodyImages.query.filter_by(post_id=id).all()
        body = Markup(current_post.body).format(imgs=imgs)
        current_post.date = current_post.date.strftime("%B %d, %Y")
        return render_template("post.html", post=current_post, body=body)


    @app.route("/<category>", methods=["GET"])
    def post_layout(category):
        """
        Renders a list of all the posts in a given category.
        """
        posts = Posts.query.filter_by(category=category).order_by(Posts.id.desc()).all()
        for post in posts:
            post.date = post.date.strftime("%B %d, %Y")
        return render_template("post_layout.html", posts=posts, category=category)


    @app.route("/subscribe", methods=['POST'])
    def subscribe():
        """
        Adds people to the subscribers database.
        """
        first = request.form["first"]
        last = request.form["last"]
        email = request.form["email"]
        if Subscribers.query.filter_by(email=email).first():
            return "Sorry this email is already subscribed"
        data = Subscribers(first, last, email)
        db.session.add(data)
        db.session.commit()

        # send them a welcome email
        subject = "Hi, it's Kelly"
        msg = Message(subject, sender=os.getenv("MAIL_USERNAME"), recipients=[email])
        msg.body = f"Hello {first},\nThanks for subscribing!\nBest,\n Kelly"
        msg.html = render_template("/emails/welcome.html", name=first)
        mail.send(msg)

        # have this automatically send a welcome email to confirm people.
        # maybe this should return some URL so we know that the person is subscribed?
        return "", 204


    @app.route('/rss')
    def rss():
        posts = Posts.query.all()
        xml = render_template("rss.xml", posts=posts)
        return Response(xml, mimetype='text/xml')

    return app
