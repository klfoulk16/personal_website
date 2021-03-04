from flask import Flask
import os
from application.database import db, Admin
from application.admin import mail
from flask_migrate import Migrate

"""
App Configuration
"""

migrate = Migrate()

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

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    # Register Blueprints

    from . import admin, blog
    app.register_blueprint(admin.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
