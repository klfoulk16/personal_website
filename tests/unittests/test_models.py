import pytest

def test_posts_model():
    """
    GIVEN a Posts model
    WHEN a new Post is created
    THEN check the h1, header_path, youtube_vid, sample, body, category, and date fields are defined correctly
    """
    pass


def test_body_images():
    """
    GIVEN a Body Images model
    WHEN a new Body Image is created
    THEN check the post_id and img_path fields are defined correctly
    """
    pass


def test_subscribers():
    """
    GIVEN a Subscribers model
    WHEN a new Subscriber is created
    THEN check the first, last, email, and date_subscribed fields are defined correctly
    """
    pass


def test_admin():
    """
    GIVEN a Admin model
    WHEN a new Admin is created
    THEN check the email, password_hash and authenticated fields are defined correctly
    """
    pass


def test_admin():
    """
    GIVEN a Admin model
    WHEN a new Admin is created
    THEN check the check_password, is_active, get_id, is_authenticated and is_anonymous methods are defined correctly
    """
    pass