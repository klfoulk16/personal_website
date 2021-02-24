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
from database import db, Admin, Posts, Subscribers, BodyImages

"""
App Configuration
"""

# Load environment variables
load_dotenv()

mail = Mail()
login_manager = LoginManager()


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

    @login_manager.user_loader
    def load_user(user_id):
        """
        Given a unique user_id (email), return the associated User object.
        """
        return Admin.query.get(user_id)

    """
    App Routes
    """

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
        msg = Message(subject, sender="kellyfoulkblog@gmail.com", recipients=[email])
        msg.body = f"Hello {first},\n Thanks for subscribing! \n Best, \n Kelly"
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


    """
    Admin-only Routes.
    """

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """
        Logs a user in (given the email and password are correct).
        """
        if current_user.is_authenticated:
            return redirect(url_for("admin"))
        if request.method == "POST":
            email = request.form["email"]
            user = Admin.query.get(email)
            if user is not None and user.check_password(request.form["password"]):
                login_user(user)
                flash("What would you like to do today?")
                return redirect(url_for("admin"))
            return render_template("login.html", message="Username or password incorrect.")
        else:
            return render_template("login.html")


    @app.route("/logout")
    @login_required
    def logout():
        """
        Logs a user out of the app.
        """
        logout_user()
        return redirect(url_for("index"))


    @app.route("/create", methods=["GET", "POST"])
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
                img_folder = os.path.join("static", "post_imgs", post_id)
                if not os.path.exists(img_folder):
                    os.makedirs(img_folder)
                header_path = os.path.join(img_folder, header.filename)
                header.save(header_path)
            else:
                header_path = None
            # h1, sample, header_path, youtube_vid, body, category
            data = Posts(h1, sample, header_path, youtube_vid, body, category)
            db.session.add(data)
            for img in request.files.getlist("body_imgs"):
                if img.filename != "":
                    img_folder = os.path.join("static", "post_imgs", post_id)
                    if not os.path.exists(img_folder):
                        os.makedirs(img_folder)
                    img_location = os.path.join(img_folder, img.filename)
                    img.save(img_location)
                    img_data = BodyImages(post_id, img_location)
                    db.session.add(img_data)
            db.session.commit()
            flash("Success, your post is live.")
            return redirect(url_for("admin"))

        else:
            return render_template("create.html", post_id=post_id)


    @app.route("/edit/<id>", methods=["GET", "POST"])
    @login_required
    def edit(id):
        post = Posts.query.filter_by(id=id).first()
        if request.method == "GET":
            return render_template("edit.html", post=post)
        else:
            post.h1 = request.form["h1"]
            post.sample = request.form["sample"]
            post.youtube_vid = request.form["youtube_vid"]
            post.body = request.form["body"]
            header = request.files["header"]
            if header.filename != "":
                img_folder = os.path.join("static", "post_imgs", id)
                if not os.path.exists(img_folder):
                    os.makedirs(img_folder)
                post.header_path = os.path.join(img_folder, header.filename)
                header.save(post.header_path)
            db.session.commit()
            flash("Success, the post has been updated.")
            return redirect(url_for("admin"))


    @app.route("/admin", methods=["GET"])
    @login_required
    def admin():
        """
        Renders the admin panel.
        """
        return render_template("admin.html")


    # send email to all marinas
    @app.route("/send-mail", methods=["GET", "POST"])
    @login_required
    def send_mail():
        """
        The user can send out email updates - as well as see a rough preview of what the
        email html may look like and send out a test email.
        """
        if request.method == "POST":
            # get list of all marina's info
            subs = Subscribers.query.filter_by(still_subscribed=True).all()
            # get the email information
            subject = request.form["subject"]
            body_text = request.form["body_text"]
            body_html = request.form["body_html"]
            for sub in subs:
                msg = Message(
                    subject, sender="kellyfoulkblog@gmail.com", recipients=[sub.email]
                )
                msg.body = f"Hello {sub.first},\n{body_text}"
                msg.html = Markup(body_html).format(name=sub.first)
                mail.send(msg)
            flash("Success, the mail has been sent.")
            return redirect(url_for("admin"))
        else:
            return render_template("send-mail.html")


    @app.route("/send-test", methods=["POST"])
    @login_required
    def send_test():
        """
        Sends a test email to my email.
        """
        # get the email information
        subject = request.form["subject"]
        body_text = request.form["body_text"]
        body_html = request.form["body_html"]
        msg = Message(
            subject, sender="kellyfoulkblog@gmail.com", recipients=["klf16@my.fsu.edu"]
        )
        msg.body = body_text
        msg.html = Markup(body_html).format(name="Kelly")
        mail.send(msg)
        return "", 204

    return app
