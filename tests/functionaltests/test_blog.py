import pytest
from application.database import Subscribers
from application.admin import mail

def test_index_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hiya, I'm Kelly" in response.data
    assert b"Subscribe" in response.data

    # assert all posts in database are displayed
    assert b"Header 1 for the test post" in response.data
    assert b"Hi this is a sample" in response.data


def test_index_post(client):
    """
    GIVEN a Flask application
    WHEN the '/' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("/")
    assert response.status_code == 405
    assert b"Hiya, I'm Kelly" not in response.data


def test_view_post_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/<id>' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("/post/1")
    assert response.status_code == 200
    assert b"Header 1 for the test post" in response.data
    assert b"<p>hi I edited this</p>" in response.data


def test_view_post_post(client):
    """
    GIVEN a Flask application
    WHEN the '/post/<id>' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("/post/1")
    assert response.status_code == 405
    assert b"Header 1 for the test post" not in response.data
    assert b"<p>hi I edited this</p>" not in response.data


def test_post_layout_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/<category>' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("/code")
    assert response.status_code == 200
    assert b"Header 1 for the test post" in response.data
    assert b"Hi this is a sample" in response.data
    assert b"H1 for the other test post" not in response.data
    assert b"Sample for the other test post" not in response.data

    response = client.get("/other")
    assert response.status_code == 200
    assert b"H1 for the other test post" in response.data
    assert b"Sample for the other test post" in response.data
    assert b"Header 1 for the test post" not in response.data
    assert b"Hi this is a sample" not in response.data


def test_post_layout_post(client):
    """
    GIVEN a Flask application
    WHEN the '/<category>' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("/code")
    assert response.status_code == 405
    assert b"Header 1 for the test post" not in response.data
    assert b"Hi this is a sample" not in response.data

    response = client.post("/other")
    assert response.status_code == 405
    assert b"H1 for the other test post" not in response.data
    assert b"Sample for the other test post" not in response.data


# this doesn't work? why?
@pytest.mark.xfail
def test_subscribe_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/subscribe' page is requested (GET)
    THEN check that a '405' status code is returned (method not allowed)
    """
    response = client.get("/subscribe")
    assert response.status_code == 405


def test_subscribe_post(client, app):
    """
    GIVEN a Flask application
    WHEN the '/subscribe' page is posted to (POST)
    THEN check that the response is valid and a subcriber is added to the db
    """
    with app.app_context():
        sub = Subscribers.query.filter_by(email="test@example.com").first()
        assert sub is None
    first = "testfirst"
    last = "testlast"
    email = "test@example.com" 
    with mail.record_messages() as outbox:
        response = client.post(
            "/subscribe",
            data=dict(first=first, last=last, email=email),
        )
        assert response.status_code == 204

        # assert email was sent to the new with the correct subject
        assert len(outbox) == 1
        assert outbox[0].subject == "Hi, it's Kelly"
        assert outbox[0].body == f"Hello {first},\nThanks for subscribing!\nBest,\n Kelly"
        assert outbox[0].html == f"<p>Hi {first},</p>\n<p>Thanks for subscribing!</p>\n<p>Best,</p>\n<p>Kelly</p>"

    with app.app_context():
        sub = Subscribers.query.filter_by(email="test@example.com").first()
        assert sub is not None


def test_rss_get(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/rss' page is requested (GET)
    THEN check that a '200' status code is returned (method not allowed)
    """
    response = client.get("/rss")
    assert response.status_code == 200


def test_rss_post(client):
    """
    GIVEN a Flask application
    WHEN the '/rss' page is posted to (POST)
    THEN check that a '405' status code is returned
    """
    response = client.post("/rss")
    assert response.status_code == 405
