from pytwitcher import twitch
from conftest import assert_channel_equals_json


def test_wrap_json(channel1json):
    c = twitch.Channel.wrap_json(channel1json)
    assert_channel_equals_json(c, channel1json)


def test_wrap_search(search_channels_response, channel1json, channel2json):
    channels = twitch.Channel.wrap_search(search_channels_response)
    for c, j in zip(channels, [channel1json, channel2json]):
        assert_channel_equals_json(c, j)


def test_wrap_get_channel(get_channel_response, channel1json):
    c = twitch.Channel.wrap_get_channel(get_channel_response)
    assert_channel_equals_json(c, channel1json)
