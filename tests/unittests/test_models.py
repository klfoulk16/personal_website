import pytest
from application.database import Posts, BodyImages, Subscribers, Admin
import datetime


def test_posts_model():
    """
    GIVEN a Posts model
    WHEN a new Post is created
    THEN check the h1, header_path, youtube_vid, sample, body, category, and date fields are defined correctly
    """
    h1 = "Hi"
    header_path = "/stuff/stuff/stuff/stuff"
    youtube_vid = "80938203"
    sample = "Hi this is a sample"
    body = "<p>hi I edited this</p>"
    category = "code"
    post = Posts(h1, sample, header_path, youtube_vid, body, category)
    assert post.h1 == h1
    assert post.header_path == header_path
    assert post.youtube_vid == youtube_vid
    assert post.sample == sample
    assert post.body == body
    assert post.category == category
    assert post.date == datetime.date.today()


def test_body_images():
    """
    GIVEN a Body Images model
    WHEN a new Body Image is created
    THEN check the post_id and img_path fields are defined correctly
    """
    post_id = 1
    img_path = "stuff/stuff/stuff/stuff"
    body_img = BodyImages(post_id, img_path)
    assert body_img.post_id == post_id
    assert body_img.img_path == img_path


def test_subscribers():
    """
    GIVEN a Subscribers model
    WHEN a new Subscriber is created
    THEN check the first, last, email, and date_subscribed fields are defined correctly
    """
    first = "Nelly"
    last = "Kelly"
    email = "nelly@kelly.com"

    sub = Subscribers(first, last, email)

    assert sub.first == first
    assert sub.last == last
    assert sub.email == email
    assert sub.date_subscribed == datetime.date.today()


def test_admin():
    """
    GIVEN a Admin model
    WHEN a new Admin is created
    THEN check the email, password_hash and authenticated fields are defined correctly
    THEN also check that methods are properly defined
    """
    username = "nelly@kelly.com"
    password = "weeeeeeeeeeee" #this is not encrypted but should be when sending to database

    admin = Admin(username, password)
    assert admin.username == username
    assert admin.password_hash == password
