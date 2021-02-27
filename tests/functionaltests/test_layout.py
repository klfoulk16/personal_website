"""Attempting to test the fact that the layout is at the top of routes properly with subscribe modal."""

import pytest

def test_layout_visibility(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("/")
    assert response.status_code == 200
    # assert layout is properly displayed
    assert b"Subscribe" in response.data
    assert b"Kelly Foulk" in response.data

    # check to see if hidden modal is there
    assert b"Let's stay in touch!" in response.data