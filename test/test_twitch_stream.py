import mock
import pytest
from requests.sessions import Session

from pytwitcher import twitch
from test import conftest


def test_wrap_json(stream1json):
    s = twitch.Stream.wrap_json(stream1json)
    conftest.assert_stream_equals_json(s, stream1json)


def test_repr(stream1json):
    s = twitch.Stream.wrap_json(stream1json)
    assert repr(s) == '<Stream %s, id: %s>' % (s.channel.name, s.twitchid)


def test_wrap_search(search_streams_response, stream1json, stream2json):
    streams = twitch.Stream.wrap_search(search_streams_response)
    for s, j in zip(streams, [stream1json, stream2json]):
        conftest.assert_stream_equals_json(s, j)


def test_wrap_get_stream(get_stream_response, stream1json):
    s = twitch.Stream.wrap_get_stream(get_stream_response)
    conftest.assert_stream_equals_json(s, stream1json)


def test_wrap_get_offline_stream(get_offline_stream_response):
    s = twitch.Stream.wrap_get_stream(get_offline_stream_response)
    assert s is None


@pytest.fixture(scope="function")
def mock_fetch_viewers(monkeypatch):
    monkeypatch.setattr(twitch.Game, "fetch_viewers", mock.Mock())


def test_get_game(stream1json, game1json, games_search_response, mock_session,
                  mock_fetch_viewers):
    Session.request.return_value = games_search_response
    s = twitch.Stream.wrap_json(stream1json)
    g = s.get_game()
    conftest.assert_game_equals_json(g, game1json)
