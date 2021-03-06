"""Blueprint for the admin side of the app"""

from flask import (
    flash,
    render_template,
    request,
    redirect,
    url_for,
    Markup,
    Blueprint,
    abort,
    session
)
from flask_mail import Mail, Message
import os
from application.database import db, Admin, Posts, Subscribers, BodyImages
from werkzeug.security import check_password_hash
import functools

bp = Blueprint('admin', __name__, url_prefix='/admin')

mail = Mail()

def login_required(view):
    """
    Creates wrap that prevents unlogged in viewers from accessing admin-only routes.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('admin.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Logs a user in (given the email and password are correct).
    """
    if request.method == "POST":
        username = request.form["username"]
        user = Admin.query.get(username)
        if user is not None and check_password_hash(user.password_hash, (request.form["password"])):
            session.clear()
            session['user_id'] = user.username
            flash("What would you like to do today?")
            return redirect(url_for("admin.admin"))
        return render_template("admin/login.html", message="Username or password incorrect.")
    elif session.get('user_id') is not None:
        return redirect(url_for("admin.admin"))
    else:
        return render_template("admin/login.html")


@bp.route("/logout")
@login_required
def logout():
    """
    Logs a user out of the app.
    """
    session.clear()
    return redirect(url_for("index"))


@bp.route("/", methods=["GET"])
@login_required
def admin():
    """
    Renders the admin panel.
    """
    return render_template("admin/admin.html")


@bp.route("/styles")
@login_required
def base_styles():
    """
    Displays examples of some core CSS styles.
    """
    return render_template("admin/base-styles.html")


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """
    Get: renders the screen where the user can create a new post.
    Post: Adds the new post's information to the post and body images database.
    """
    post_id = Posts.query.order_by(Posts.id.desc()).first()
    if post_id:
        post_id = str(int(post_id.id) + 1)
    else:
        post_id = "1"
    if request.method == "POST":
        h1 = request.form["h1"]
        sample = request.form["sample"]
        youtube_vid = request.form["youtube_vid"]
        body = request.form["body"]
        print(body)
        category = request.form["category"]
        header = request.files["header"]
        if header.filename != "":
            # image folder and save location need to be usable from top level of directory
            img_folder = os.path.join("application", "static", "post_imgs", post_id)
            if not os.path.exists(img_folder):
                os.makedirs(img_folder)
            header.save(os.path.join(img_folder, header.filename))
            # 'header_path' assumes we're in the 'templates' directory
            header_path = os.path.join("static", "post_imgs", post_id, header.filename)
        else:
            header_path = None
        # h1, sample, header_path, youtube_vid, body, category
        data = Posts(h1, sample, header_path, youtube_vid, body, category)
        db.session.add(data)
        for img in request.files.getlist("body_imgs"):
            if img.filename != "":
                # image folder and save location need to be usable from top level of directory
                img_folder = os.path.join("application", "static", "post_imgs", post_id)
                if not os.path.exists(img_folder):
                    os.makedirs(img_folder)
                img.save(os.path.join(img_folder, img.filename))
                # img_path assumes we're in the 'templates' directory
                img_path = os.path.join("static", "post_imgs", post_id, img.filename)
                img_data = BodyImages(post_id, img_path)
                db.session.add(img_data)
        db.session.commit()
        flash("Success, your post is live.")
        return redirect(url_for("admin.admin"))

    else:
        return render_template("admin/create.html", post_id=post_id)


@bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Posts.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("admin/edit.html", post=post)
    else:
        post.h1 = request.form["h1"]
        post.sample = request.form["sample"]
        post.youtube_vid = request.form["youtube_vid"]
        post.body = request.form["body"]
        header = request.files["header"]
        if header.filename != "":
            # image folder and save location need to be usable from top level of directory
            img_folder = os.path.join("application", "static", "post_imgs", id)
            if not os.path.exists(img_folder):
                os.makedirs(img_folder)
            header.save(os.path.join(img_folder, header.filename))
            # 'header_path' assumes we're in the 'templates' directory
            post.header_path = os.path.join("static", "post_imgs", id, header.filename)
        db.session.commit()
        flash("Success, the post has been updated.")
        return redirect(url_for("admin.admin"))


@bp.route("/send-mail", methods=["GET", "POST"])
@login_required
def send_mail():
    """
    The user can send out email updates - as well as see a rough preview of what the
    email html may look like and send out a test email.
    """
    if request.method == "POST":
        subs = Subscribers.query.filter_by(still_subscribed=True).all()
        subject = request.form["subject"]
        body_text = request.form["body_text"]
        body_html = request.form["body_html"]
        for sub in subs:
            msg = Message(
                subject, sender=os.getenv("MAIL_USERNAME"), recipients=[sub.email]
            )
            msg.body = f"Hello {sub.first},\n{body_text}"
            msg.html = Markup(body_html).format(name=sub.first)
            mail.send(msg)
        flash("Success, the mail has been sent.")
        return redirect(url_for("admin.admin"))
    else:
        return render_template("admin/send-mail.html")


@bp.route("/send-test", methods=["POST"])
@login_required
def send_test():
    """
    Sends a test email to my email.
    """
    if 'user_id' not in session:
        abort(401)
    subject = request.form["subject"]
    body_text = request.form["body_text"]
    body_html = request.form["body_html"]
    msg = Message(
        subject, sender=os.getenv("MAIL_USERNAME"), recipients=[os.getenv("TEST_EMAIL")]
    )
    msg.body = body_text
    msg.html = Markup(body_html).format(name="Kelly")
    mail.send(msg)
    return "", 204