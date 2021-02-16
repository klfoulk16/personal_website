import pytest
from app import app
import io

@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def post_to_upload():
    """Post with empty header image"""
    return dict(
        h1="This is the test post",
        header=('', ''),
        youtube_vid="02834ohreuw923",
        sample="Want to learn pandas, but don't know where to start?",
        body="""<p>Want to learn pandas, but don't know where to start? That was my position about a week ago. In this post, I'll explain how I structured my learning process during my one week 'crash course.' By no means am I an expert now, but I feel confident to say I can accomplish essential data cleaning and visualization tasks.</p>

<p>You can find the git repository and associated Jupyter notebooks <a href='https://github.com/klfoulk16/learning_pandas'>here.</a></p>

<h2>My Learning Process</h2>""",
        category="Other",
        body_imgs=[]
    )

@pytest.fixture
def post_to_upload2():
    """Post with a header image"""
    return dict(
        h1="This is the second test post",
        header= (io.BytesIO(b"abcdef"), 'test.jpg'),
        youtube_vid="02834ohreuw923",
        sample="Want to learn pandas, but don't know where to start?",
        body="<p>Want to learn pandas, but don't know where to start?</p>",
        category="Other",
        body_imgs=[]
    )