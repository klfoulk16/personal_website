"""Blueprint for the user-facing blog side of the app"""

from flask import (
    render_template,
    request,
    Markup,
    Response,
    Blueprint
)
import os
from application.database import db, Posts, Subscribers, BodyImages
from application.admin import mail
from flask_mail import Message

bp = Blueprint('blog', __name__)

@bp.route("/", methods=["GET"])
def index():
    """
    Renders the main home page of the blog - including a short display of all posts.
    """
    posts = Posts.query.order_by(Posts.id.desc()).all()
    for post in posts:
        post.date = post.date.strftime("%B %d, %Y")
        post.header = BodyImages.query.filter_by(post_id=post.id).first()
    return render_template("blog/index.html", posts=posts)


@bp.route("/post/<id>", methods=["GET"])
def view_post(id):
    """
    Renders the post with a given id (the id of the post to render is passed with the route).
    """
    current_post = Posts.query.filter_by(id=id).first()

    imgs = BodyImages.query.filter_by(post_id=id).all()
    body = Markup(current_post.body).format(imgs=imgs)
    current_post.date = current_post.date.strftime("%B %d, %Y")
    return render_template("blog/post.html", post=current_post, body=body)


@bp.route("/<category>", methods=["GET"])
def post_layout(category):
    """
    Renders a list of all the posts in a given category.
    """
    posts = Posts.query.filter_by(category=category).order_by(Posts.id.desc()).all()
    for post in posts:
        post.date = post.date.strftime("%B %d, %Y")
    return render_template("blog/post_layout.html", posts=posts, category=category)


@bp.route("/subscribe", methods=['POST'])
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


@bp.route('/rss')
def rss():
    posts = Posts.query.all()
    xml = render_template("rss.xml", posts=posts)
    return Response(xml, mimetype='text/xml')
