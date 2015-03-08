from pytwitcher import twitch
from conftest import assert_channel_equals_json


def test_wrap_json(channel1json):
    c = twitch.Channel.wrap_json(channel1json)
    assert_channel_equals_json(c, channel1json)
