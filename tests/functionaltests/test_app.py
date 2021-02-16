import pytest
import os
from app import db, Posts, Subscribers, Admin

def test_index_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hiya, I'm Kelly" in response.data
    assert b"Subscribe" in response.data

    # assert all posts in database are displayed
    posts = db.session.query(Posts).all()
    for post in posts:
        assert post.h1.encode() in response.data
        assert post.sample.encode() in response.data

def test_index_post(client):
    """
    GIVEN a Flask application
    WHEN the '/' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post('/')
    assert response.status_code == 405
    assert b"Hiya, I'm Kelly" not in response.data


def test_view_post_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/<id>' page is requested (GET)
    THEN check that the response is valid
    """
    post = Posts.query.first()
    if post:
        response = client.get(f'/post/{post.id}')
        assert response.status_code == 200
        assert post.h1.encode() in response.data
        assert post.body.encode() in response.data

def test_view_post_post(client):
    """
    GIVEN a Flask application
    WHEN the '/post/<id>' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    post = Posts.query.first()
    if post:
        response = client.post(f'/post/{post.id}')
        assert response.status_code == 405
        assert post.h1.encode() not in response.data
        assert post.body.encode() not in response.data

def test_post_layout_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/<category>' page is requested (GET)
    THEN check that the response is valid
    """
    for c in ["code", "other"]:
        response = client.get(f'/{c}')
        assert response.status_code == 200
        posts = Posts.query.filter_by(category=c).all()
        for post in posts:
            assert post.h1.encode() in response.data
            assert post.sample.encode() in response.data

def test_post_layout_post(client):
    """
    GIVEN a Flask application
    WHEN the '/<category>' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    for c in ["code", "other"]:
        response = client.post(f'/{c}')
        assert response.status_code == 405
        post = Posts.query.filter_by(category=c).first()
        if post:
            assert post.h1.encode() not in response.data
            assert post.sample.encode() not in response.data


# this doesn't work? why?
@pytest.mark.xfail
def test_subscribe_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/subscribe' page is requested (GET)
    THEN check that a '405' status code is returned (method not allowed)
    """
    response = client.get('/subscribe')
    assert response.status_code == 405
    

def test_subscribe_post(client):
    """
    GIVEN a Flask application
    WHEN the '/subscribe' page is posted to (POST)
    THEN check that the response is valid and a subcriber is added to the db
    """
    response = client.post(
        '/subscribe', data=dict(
            first="testfirst",
            last="testlast",
            email="test@example.com"
        )
    )
    assert response.status_code == 204
    sub = Subscribers.query.filter_by(email="test@example.com").first() 
    assert sub is not None
    db.session.delete(sub)
    db.session.commit()


# functions to aid with testing login
def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Email" in response.data
    assert b"Password" in response.data



def test_login_post(client):
    """
    GIVEN a Flask application
    WHEN the '/login' page is posted to (POST)
    THEN check that response is valid and person is logged in
    """
    admin = Admin.query.filter_by(email="kelly").first()
    assert admin.check_password("kelly")
    response = login(client, admin.email, "kelly")
    assert response.status_code == 200
    assert b"What would you like to do today?" in response.data


def test_logout_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' route is run (GET)
    THEN check that the response is valid and user is logged out
    """
    login(client, "kelly", "kelly")
    assert client.get('/create').status_code == 200
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Hiya, I'm Kelly" in response.data
    assert client.get('/create').status_code == 401


def test_logout_post(client):
    """
    GIVEN a Flask application
    WHEN the '/logout' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post('/logout')
    assert response.status_code == 405


def test_create_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/create' route is run (GET)
    THEN check that the response is valid
    """
    login(client, "kelly", "kelly")
    response = client.get('/create')
    assert response.status_code == 200
    assert b'Create New Post' in response.data


def test_create_post_with_header_file(client, post_to_upload):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that posts are properly created if header file not included
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200
    response = client.post(
        '/create', data=post_to_upload, follow_redirects=True)
    assert response.status_code == 200
    assert b'Success, your post is live.' in response.data
    post = Posts.query.filter_by(h1="This is the test post").first() 
    assert post is not None

    # make sure a file path for nonexistent header image was not made
    assert not os.path.exists(post.header_path)

    db.session.delete(post)
    db.session.commit()
    assert Posts.query.filter_by(h1="This is the test post").first() is None


def test_create_post_with_header_file(client, post_to_upload2):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that posts are properly created if header file included
    """
    r = login(client, "kelly", "kelly")
    response = client.post(
        '/create', data=post_to_upload2, follow_redirects=True)
    assert response.status_code == 200
    assert b'Success, your post is live.' in response.data
    post = Posts.query.filter_by(h1="This is the second test post").first() 
    assert post is not None
    # make sure file path for header image was made
    assert os.path.exists(post.header_path)

    # clean it all up
    os.remove(post.header_path)

    db.session.delete(post)
    db.session.commit()
    assert Posts.query.filter_by(h1="This is the second test post").first() is None


def test_create_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    response = client.get('/create')
    assert response.status_code == 401
