from pytwitcher import twitch
from test import conftest


def test_wrap_json(user1json):
    s = twitch.User.wrap_json(user1json)
    conftest.assert_user_equals_json(s, user1json)


def test_wrap_get_user(get_user_response, user1json):
    s = twitch.User.wrap_get_user(get_user_response)
    conftest.assert_user_equals_json(s, user1json)
