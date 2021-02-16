import pytest
from app import app
import io


# @pytest.fixture
# def app():
#     test_app = app.app.config.update(TESTING=True) 
#     # it's bad practice to update config after app is already set up
#     # that may lead to things not working properly, we'll see -- din't work
#     return test_app


@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def post_to_upload_without_file():
    """Post with empty header image"""
    return dict(
        h1="This is the test post",
        header=(io.BytesIO(b""), ''),
        youtube_vid="vid1",
        sample="Sample for post 1",
        body="""<p>This is post 1....Want to learn pandas, but don't know where to start? That was my position about a week ago. In this post, I'll explain how I structured my learning process during my one week 'crash course.' By no means am I an expert now, but I feel confident to say I can accomplish essential data cleaning and visualization tasks.</p>

<p>You can find the git repository and associated Jupyter notebooks <a href='https://github.com/klfoulk16/learning_pandas'>here.</a></p>

<h2>My Learning Process</h2>""",
        category="Other",
        body_imgs=[]
    )

@pytest.fixture
def post_to_upload_with_file():
    """Post with a header image"""
    return dict(
        h1="This is the second test post",
        header=(io.BytesIO(b"abcdef"), 'test.jpg'),
        youtube_vid="vid2",
        sample="Want to learn pandas, but don't know where to start?",
        body="<p>This is post 2...Want to learn pandas, but don't know where to start?</p>",
        category="Code",
        body_imgs=[]
    )


@pytest.fixture
def post_to_edit_without_file():
    """Post with empty header image"""
    return dict(
        h1="This is the test edit post without a file",
        header=(io.BytesIO(b""), ''),
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
        header=(io.BytesIO(b"abcdef"), 'test.jpg'),
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