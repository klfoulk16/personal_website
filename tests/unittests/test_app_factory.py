from app import create_app

"""Tests the app factory setup."""


def test_config():
    """If config is not passed, there should be some default configuration,
    otherwise the configuration should be overridden."""
    # we didn't pass the test fixture app here so
    # .testing should be false initially
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


