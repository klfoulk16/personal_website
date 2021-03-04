"""Script to Execute to Fill Staging DB with test data"""

from application import create_app
from application.database import Subscribers, Posts, db

# heroku run python --app kellyfoulk-staging -- tests/staging-app/test_data.py

app = create_app()
with app.app_context():
    sub1 = Subscribers("SubFirst", "SubLast", "test_email@email.com")
    db.session.add(sub1)

    h1 = "Header 1 for the test post"
    header_path = "/stuff/stuff/stuff/stuff"
    youtube_vid = "80938203"
    sample = "Hi this is a sample"
    body = "<p>hi I edited this</p>"
    category = "code"
    post1 = Posts(h1, sample, header_path, youtube_vid, body, category)
    db.session.add(post1)

    h1 = "H1 for the other test post"
    header_path = ""
    youtube_vid = "1111111"
    sample = "Sample for the other test post"
    body = "<p>Hi this is sample stuff for the other test post</p>"
    category = "other"
    post2 = Posts(h1, sample, header_path, youtube_vid, body, category)
    db.session.add(post2)
    
    db.session.commit()