import pytest
from app import Posts, Subscribers, BodyImages, Admin, db

"""Tests to make sure app fixtures are working properly"""

def test_app_fixture(app):
    """
    GIVEN an app fixture
    WHEN a new instance is created
    THEN check that the database is empty and insertion works properly.
    There are two of these to check the database clearing after each test.
    """
    h1 = "Hi"
    header_path = "/stuff/stuff/stuff/stuff"
    youtube_vid = "80938203"
    sample = "Hi this is a sample"
    body = "<p>hi I edited this</p>"
    category = "code"
    post = Posts(h1, sample, header_path, youtube_vid, body, category)

    with app.app_context():
        assert len(db.session.query(Posts).all()) == 2
        db.session.add(post)
        db.session.commit()
        assert len(db.session.query(Posts).all()) == 3


def test_app_fixture2(app):
    """
    GIVEN an app fixture
    WHEN a new instance is created
    THEN check that the database is empty and insertion works properly.
    There are two of these to check the database clearing after each test.
    """
    h1 = "Hi"
    header_path = "/stuff/stuff/stuff/stuff"
    youtube_vid = "80938203"
    sample = "Hi this is a sample"
    body = "<p>hi I edited this</p>"
    category = "code"
    post = Posts(h1, sample, header_path, youtube_vid, body, category)

    with app.app_context():
        assert len(db.session.query(Posts).all()) == 2
        db.session.add(post)
        db.session.commit()
        assert len(db.session.query(Posts).all()) == 3
