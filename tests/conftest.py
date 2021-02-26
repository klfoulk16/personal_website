import pytest
from application import create_app
from application.database import Admin, db, Posts, Subscribers
import io
import dotenv
import os
from tests import setup_db, teardown_db, clean_db

dotenv.load_dotenv()

@pytest.fixture
def app(codepost1, otherpost1, admin_user, subscriber1):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv("TEST_DATABASE_URL"),
    })

    # make sure db is clean to start
    with app.app_context():
        clean_db()
        db.session.add(codepost1)
        db.session.add(otherpost1)
        db.session.add(admin_user)
        db.session.add(subscriber1)
        db.session.commit()

    yield app
    
    with app.app_context():
        teardown_db()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user():
    return Admin("kelly", "kelly")


@pytest.fixture
def subscriber1():
    return Subscribers("Kelly", "Foulk", "klf16@my.fsu.edu")


@pytest.fixture
def codepost1():
    h1 = "Header 1 for the test post"
    header_path = "/stuff/stuff/stuff/stuff"
    youtube_vid = "80938203"
    sample = "Hi this is a sample"
    body = "<p>hi I edited this</p>"
    category = "code"
    return Posts(h1, sample, header_path, youtube_vid, body, category)


@pytest.fixture
def otherpost1():
    h1 = "H1 for the other test post"
    header_path = ""
    youtube_vid = "1111111"
    sample = "Sample for the other test post"
    body = "<p>Hi this is sample stuff for the other test post</p>"
    category = "other"
    return Posts(h1, sample, header_path, youtube_vid, body, category)


@pytest.fixture
def post_to_upload_without_file():
    """Post with empty header image"""
    return dict(
        h1="This is the test post",
        header=(io.BytesIO(b""), ""),
        youtube_vid="vid1",
        sample="Sample for post 1",
        body="""<p>This is post 1....Want to learn pandas, but don't know where to start? That was my position about a week ago. In this post, I'll explain how I structured my learning process during my one week 'crash course.' By no means am I an expert now, but I feel confident to say I can accomplish essential data cleaning and visualization tasks.</p>

<p>You can find the git repository and associated Jupyter notebooks <a href='https://github.com/klfoulk16/learning_pandas'>here.</a></p>

<h2>My Learning Process</h2>""",
        category="Other",
        body_imgs=[],
    )


@pytest.fixture
def post_to_upload_with_file():
    """Post with a header image"""
    return dict(
        h1="This is the second test post",
        header=(io.BytesIO(b"abcdef"), "test.jpg"),
        youtube_vid="vid2",
        sample="Want to learn pandas, but don't know where to start?",
        body="<p>This is post 2...Want to learn pandas, but don't know where to start?</p>",
        category="Code",
        body_imgs=[],
    )


@pytest.fixture
def post_to_edit_without_file():
    """Post with empty header image"""
    return dict(
        h1="This is the test edit post without a file",
        header=(io.BytesIO(b""), ""),
        youtube_vid="videdited",
        sample="Sample for edited post without file",
        body="""<p>This is the test edit post without a file....Want to learn pandas, but don't know where to start? That was my position about a week ago. In this post, I'll explain how I structured my learning process during my one week 'crash course.' By no means am I an expert now, but I feel confident to say I can accomplish essential data cleaning and visualization tasks.</p>

<p>You can find the git repository and associated Jupyter notebooks <a href='https://github.com/klfoulk16/learning_pandas'>here.</a></p>

<h2>My Learning Process</h2>""",
    )


@pytest.fixture
def post_to_edit_with_file():
    """Post with a header image"""
    return dict(
        h1="This is the test edit post with a file",
        header=(io.BytesIO(b"abcdef"), "test.jpg"),
        youtube_vid="vid2",
        sample="Sample for post with file",
        body="<p>This is the test edit post with a file...Want to learn pandas, but don't know where to start?</p>",
    )


@pytest.fixture
def email():
    """Email for use with the send/test email routes"""
    return dict(
        subject="Fake Email Subject",
        body_text="Hi {name}, This is the text of the message",
        body_html="<p>Hi {name},</p><p>This is the text of the message</p>",
    )
