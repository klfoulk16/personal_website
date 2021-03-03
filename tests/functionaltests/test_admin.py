"""Tests for all the routes in the admin blueprint"""
import pytest
import os
from application.database import Posts, Subscribers, Admin
from application.admin import mail

# functions to aid with testing login
def login(client, email, password):
    return client.post(
        "admin/login", data=dict(email=email, password=password), follow_redirects=True
    )


def logout(client):
    return client.get("admin/logout", follow_redirects=True)


def test_login_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("admin/login")
    assert response.status_code == 200
    assert b"Email" in response.data
    assert b"Password" in response.data


def test_login_post(client, app):
    """
    GIVEN a Flask application
    WHEN the '/login' page is posted to (POST)
    THEN check that response is valid and person is logged in
    """
    response = client.post(
        "admin/login", data={"email": "kelly", "password": "kelly"}, follow_redirects=True
        )
    assert response.status_code == 200
    assert b"What would you like to do today?" in response.data


def test_logout_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' route is run (GET)
    THEN check that the response is valid and user is logged out
    """
    login(client, "kelly", "kelly")
    assert client.get("admin/create").status_code == 200
    response = client.get("admin/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Hiya, I'm Kelly" in response.data
    assert client.get("admin/create").status_code == 401


def test_logout_post(client):
    """
    GIVEN a Flask application
    WHEN the '/logout' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("admin/logout")
    assert response.status_code == 405


def test_create_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/create' route is run (GET)
    THEN check that the response is valid
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200  # test will fail is this doesn't work
    response = client.get("admin/create")
    assert response.status_code == 200
    assert b"Create New Post" in response.data


def test_create_post_without_header_file(client, post_to_upload_without_file, app):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that posts are properly created if header file not included
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200  # test will fail is this doesn't work
    response = client.post(
        "admin/create", data=post_to_upload_without_file, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Success, your post is live." in response.data

    with app.app_context():
        post = Posts.query.filter_by(h1="This is the test post").first()
        assert post is not None


def test_create_post_with_header_file(client, post_to_upload_with_file, app):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that posts are properly created if header file included
    """
    # this test will only work if run from root personal_website directory, so let's check that
    assert os.path.split(os.getcwdb())[1] == b'personal_website'

    r = login(client, "kelly", "kelly")
    assert r.status_code == 200  # test will fail is this doesn't work

    response = client.post(
        "admin/create", data=post_to_upload_with_file, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Success, your post is live." in response.data
    with app.app_context():
        post = Posts.query.filter_by(h1="This is the second test post").first()
        assert post is not None
        # make sure file path for header image was made
        assert os.path.exists(os.path.join("application", post.header_path))

    # clean image up
    os.remove(os.path.join("application", post.header_path))
    # clean extra directory
    try:
        os.rmdir(os.path.join("application", "static", "post_imgs", str(post.id)))
    except OSError as e:
        pass  # directory not empty because actually posts are using it


def test_create_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/create' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    response = client.get("admin/create")
    assert response.status_code == 401


def test_edit_post_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/edit' route is run (GET)
    THEN check that the response is valid if page exists
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200  # test will fail is this doesn't work
    # get the edit page
    response = client.get("admin/edit/1")
    assert response.status_code == 200
    assert b"Edit" in response.data


@pytest.mark.xfail
def test_edit_nonexistant_post_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/edit' route is run (GET)
    THEN check that the response is not valid if page does not exist
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200  # test will fail if this doesn't work
    # get the edit page
    response = client.get("admin/edit/100")
    assert response.status_code == 404  # not found
    assert b"This post does not exist" in response.data


def test_edit_post_with_no_header_files(app, client, post_to_upload_without_file, post_to_edit_without_file):
    """
    GIVEN a Flask application
    WHEN the '/edit/<id>' page is posted to (POST)
    THEN check that post is properly edited
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    # create post to edit
    response = client.post(
        "admin/create", data=post_to_upload_without_file, follow_redirects=True
    )

    with app.app_context():
        orig_post = Posts.query.filter_by(h1="This is the test post").first()

    response = client.post(
        f"admin/edit/{orig_post.id}", data=post_to_edit_without_file, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Success, the post has been updated." in response.data
    with app.app_context():
        assert Posts.query.filter_by(h1="This is the test post").first() is None

        post = Posts.query.filter_by(h1="This is the test edit post without a file").first()
        assert post is not None
        assert post.youtube_vid == "videdited"
        assert post.sample == "Sample for edited post without file"
        assert post.body == """<p>This is the test edit post without a file....Want to learn pandas, but don't know where to start? That was my position about a week ago. In this post, I'll explain how I structured my learning process during my one week 'crash course.' By no means am I an expert now, but I feel confident to say I can accomplish essential data cleaning and visualization tasks.</p>

<p>You can find the git repository and associated Jupyter notebooks <a href='https://github.com/klfoulk16/learning_pandas'>here.</a></p>

<h2>My Learning Process</h2>"""


def test_edit_post_with_header_file(app, client, post_to_upload_without_file, post_to_edit_with_file):
    """
    GIVEN a Flask application
    WHEN the '/edit/<id>' page is posted to (POST)
    THEN check that posts are properly edited if header file is added
    """
    # this test will only work if run from root personal_website directory, so let's check that
    assert os.path.split(os.getcwdb())[1] == b'personal_website'

    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    # create post to edit
    response = client.post(
        "admin/create", data=post_to_upload_without_file, follow_redirects=True
    )
    with app.app_context():
        orig_post = Posts.query.filter_by(h1="This is the test post").first()

    response = client.post(
        f"admin/edit/{orig_post.id}", data=post_to_edit_with_file, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Success, the post has been updated." in response.data

    with app.app_context():
        assert Posts.query.filter_by(h1="This is the test post").first() is None

        post = Posts.query.filter_by(h1="This is the test edit post with a file").first()
        assert post is not None

    # make sure file path for header image was made
    assert os.path.exists(os.path.join("application", post.header_path))

    # clean image up
    os.remove(os.path.join("application", post.header_path))
    # clean extra directory
    try:
        os.rmdir(os.path.join("application", "static", "post_imgs", str(post.id)))
    except OSError as e:
        pass  # directory not empty because actually posts are using it



def test_edit_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/edit/<id>' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    # get the edit page
    response = client.get("admin/edit/1")
    assert response.status_code == 401


def test_admin_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/admin page is requested (GET)
    THEN check that the response is valid
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"Howdy!" in response.data
    assert b"Create Post" in response.data
    assert b"Edit Post" in response.data
    assert b"Delete Post" in response.data
    assert b"Send Mail" in response.data


def test_admin_post(client):
    """
    GIVEN a Flask application
    WHEN the '/admin page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("/admin/")
    assert response.status_code == 405
    assert b"Howdy!" not in response.data


def test_admin_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/admin' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    response = client.get("/admin/")
    assert response.status_code == 401


def test_send_mail_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/send-mail page is requested (GET)
    THEN check that the response is valid
    """
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    response = client.get("admin/send-mail")
    assert response.status_code == 200
    assert b"Send New Email" in response.data


#@pytest.mark.skip
def test_send_mail_post(client, email, app):
    """
    GIVEN a Flask application
    WHEN the '/send-mail page is posted to (POST)
    THEN check that a 200 status code is returned and proper number of emails are sent
    """
    assert app.testing is True
    # make sure the database is set up correctly
    with app.app_context():
        sub = Subscribers.query.filter_by(first="SubFirst").first()
        assert sub is not None
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200
    with mail.record_messages() as outbox:
        response = client.post("admin/send-mail", data=email, follow_redirects=True)
        assert response.status_code == 200
        assert b"Success, the mail has been sent." in response.data

        # assert email was sent to the one subscriber in the db with the correct subject
        assert len(outbox) == 1
        assert outbox[0].subject == "Fake Email Subject"
        assert outbox[0].body == f"Hello {sub.first},\nThis is the text of the message"
        assert outbox[0].html == f"<p>Hi {sub.first},</p><p>This is the text of the message</p>"

def test_send_mail_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/send-mail' page is posted to (POST)
    THEN check that a '401' not authorized status code is returned
    """
    response = client.get("admin/send-mail")
    assert response.status_code == 401


def test_send_test_mail_get(client):
    """
    GIVEN a Flask application
    WHEN the '/send-test page is requested (GET)
    THEN check that a '405' status code is returned
    """
    # despite being a post only route, this still returns a page
    response = client.get("admin/send-test")
    assert response.status_code == 405


def test_send_test_mail_post(client, email):
    """
    GIVEN a Flask application
    WHEN the '/send-test page is posted to (POST)
    THEN check that a 204 status code is returned
    """
    # eventually this will be a more comprehensive test
    # track that the proper number of emails are sent? not right now with current setup
    r = login(client, "kelly", "kelly")
    assert r.status_code == 200

    with mail.record_messages() as outbox:
        response = client.post("admin/send-test", data=email, follow_redirects=True)
        assert response.status_code == 204

        # assert email was sent to the one subscriber in the db with the correct subject
        assert len(outbox) == 1
        assert outbox[0].subject == "Fake Email Subject"


def test_send_test_mail_auth(client):
    """
    GIVEN a Flask application
    WHEN the '/send-test' page is posted to (POST) when a user is not authenticated
    THEN check that a '401' not authorized status code is returned
    """
    response = client.post("admin/send-test")
    assert response.status_code == 401
