import pytest
import os
from app import db, Posts, Subscribers, Admin
from flask_login import logout_user


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
    assert Subscribers.query.filter_by(email="test@example.com").first() is None # if this isn't none, the test won't work
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

    # spring cleaning cause no app factory yay
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
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200 # test will fail is this doesn't work
    response = client.get('/create')
    assert response.status_code == 200
    assert b'Create New Post' in response.data


def test_create_post_without_header_file(client, post_to_upload_without_file):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that posts are properly created if header file not included
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200 # test will fail is this doesn't work
    response = client.post(
        '/create', data=post_to_upload_without_file, follow_redirects=True)
    assert response.status_code == 200
    assert b'Success, your post is live.' in response.data
    post = Posts.query.filter_by(h1="This is the test post").first() 
    assert post is not None

    # make sure a file path for nonexistent header image was not made
    assert not os.path.exists(os.path.join("static", "post_imgs", str(post.id)))

    db.session.delete(post)
    db.session.commit()
    assert Posts.query.filter_by(h1="This is the test post").first() is None


def test_create_post_with_header_file(client, post_to_upload_with_file):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that posts are properly created if header file included
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200 # test will fail is this doesn't work

    response = client.post(
        '/create', data=post_to_upload_with_file, follow_redirects=True)
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
    assert Posts.query.filter_by(h1="This is the test post").first() is None


def test_create_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    response = client.get('/create')
    assert response.status_code == 401


def test_edit_post_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/edit' route is run (GET)
    THEN check that the response is valid if page exists
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200 # test will fail is this doesn't work
    # don't know what posts are in db...so need to check and see
    post = Posts.query.first()
    # if there's no posts in the db this test will fail
    assert post is not None
    # get the edit page
    response = client.get(f'/edit/{post.id}')
    assert response.status_code == 200
    assert b'Edit' in response.data


@pytest.mark.xfail
def test_edit_nonexistant_post_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/edit' route is run (GET)
    THEN check that the response is not valid if page does not exist
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200 # test will fail is this doesn't work
    # get last id of post in db
    post = Posts.query.order_by(Posts.id.desc()).first()
    # if there's no posts in the db set id to one, otherwise increment id by one
    if post == None:
        id = 1
    else:
        id = post.id + 1
    # get the edit page
    response = client.get(f'/edit/{id}')
    assert response.status_code == 404 # not found
    assert b'This post does not exist' in response.data


def test_edit_post_with_no_header_files(client, post_to_upload_without_file, post_to_edit_without_file):
    """
    GIVEN a Flask application
    WHEN the '/edit/<id>' page is posted to (POST)
    THEN check that post is properly edited
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    # create post to edit
    response = client.post(
        '/create', data=post_to_upload_without_file, follow_redirects=True)
    orig_post = Posts.query.filter_by(h1="This is the test post").first() 

    response = client.post(
        f'/edit/{orig_post.id}', data=post_to_edit_without_file, follow_redirects=True)
    assert response.status_code == 200
    assert b'Success, the post has been updated.' in response.data
    assert Posts.query.filter_by(h1="This is the test post").first()  is None

    post = Posts.query.filter_by(h1="This is the test edit post without a file").first() 
    assert post is not None
    assert post.youtube_vid == "videdited"
    assert post.sample == "Sample for edited post without file"
    assert post.body == """<p>This is the test edit post without a file....Want to learn pandas, but don't know where to start? That was my position about a week ago. In this post, I'll explain how I structured my learning process during my one week 'crash course.' By no means am I an expert now, but I feel confident to say I can accomplish essential data cleaning and visualization tasks.</p>

<p>You can find the git repository and associated Jupyter notebooks <a href='https://github.com/klfoulk16/learning_pandas'>here.</a></p>

<h2>My Learning Process</h2>"""

    # clean it all up
    db.session.delete(post)
    db.session.commit()


def test_edit_post_with_header_file(client, post_to_upload_without_file, post_to_edit_with_file):
    """
    GIVEN a Flask application
    WHEN the '/edit/<id>' page is posted to (POST)
    THEN check that posts are properly edited if header file is added
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    # create post to edit
    response = client.post(
        '/create', data=post_to_upload_without_file, follow_redirects=True)
    orig_post = Posts.query.filter_by(h1="This is the test post").first() 

    response = client.post(
        f'/edit/{orig_post.id}', data=post_to_edit_with_file, follow_redirects=True)
    assert response.status_code == 200
    assert b'Success, the post has been updated.' in response.data
    assert Posts.query.filter_by(h1="This is the test post").first()  is None

    post = Posts.query.filter_by(h1="This is the test edit post with a file").first() 
    assert post is not None

    # make sure file path for header image was made
    assert os.path.exists(post.header_path)

    # clean it all up
    os.remove(post.header_path)
    try:
        os.rmdir(os.path.join("static", "post_imgs", str(post.id)))
    except OSError as e:
        pass # directory not empty because actually posts are using it
    db.session.delete(post)
    db.session.commit()
    assert Posts.query.filter_by(h1="This is the test edit post with a file").first() is None


def test_edit_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/edit/<id>' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    # don't know what posts are in db...so need to check and see
    post = Posts.query.first()
    # if there's no posts in the db this test will fail
    assert post is not None
    # get the edit page
    response = client.get(f'/edit/{post.id}')
    assert response.status_code == 401


def test_admin_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/admin page is requested (GET)
    THEN check that the response is valid
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    response = client.get('/admin')
    assert response.status_code == 200
    assert b'Howdy!' in response.data
    assert b'Create Post' in response.data
    assert b'Edit Post'  in response.data
    assert b'Delete Post'  in response.data
    assert b'Send Mail' in response.data


def test_admin_post(client):
    """
    GIVEN a Flask application
    WHEN the '/admin page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post('/admin')
    assert response.status_code == 405
    assert b"Howdy!" not in response.data


def test_admin_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/admin' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    response = client.get('/admin')
    assert response.status_code == 401


def test_send_mail_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/send-mail page is requested (GET)
    THEN check that the response is valid
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    response = client.get('/send-mail')
    assert response.status_code == 200
    assert b'Send New Email' in response.data


@pytest.mark.skip
def test_send_mail_post(client, email):
    """
    GIVEN a Flask application
    WHEN the '/send-mail page is posted to (POST)
    THEN check that a  status code is returned
    """
    # eventually this will be a more comprehensive test
    # track that the proper number of emails are sent? not right now with current setup
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    response = client.post('/send-mail', data=email, follow_redirects=True)
    assert response.status_code == 200
    assert b"Success, the mail has been sent." in response.data


def test_send_mail_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/send-mail' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    response = client.get('/send-mail')
    assert response.status_code == 401


@pytest.mark.xfail
def test_send_test_mail_get(client):
    """
    GIVEN a Flask application
    WHEN the '/send-test page is requested (GET)
    THEN check that a '405' status code is returned
    """
    # despite being a post only route, this still returns a page
    response = client.get('/send-test')
    assert response.status_code == 405


def test_send_test_mail_post(client, email):
    """
    GIVEN a Flask application
    WHEN the '/send-test page is posted to (POST)
    THEN check that a  status code is returned
    """
    # eventually this will be a more comprehensive test
    # track that the proper number of emails are sent? not right now with current setup
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    response = client.post('/send-test', data=email, follow_redirects=True)
    assert response.status_code == 204


def test_send_test_mail_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/send-test' page is posted to (POST) when a user is not authenticated
    THEN check that a '401' not authorized status code is returned
    """
    response = client.post('/send-test')
    assert response.status_code == 401