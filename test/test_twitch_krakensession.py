import pytest
import mock
from requests.sessions import Session

from pytwitcher import twitch
from test import conftest


def test_request(mock_session):
    ks = twitch.KrakenSession()
    url = "hallo"
    ks.request("GET", url)
    Session.request.assert_called_with("GET", twitch.TWITCH_KRAKENURL + url)
    assert ks.headers['Accept'] == twitch.TWITCH_HEADER_ACCEPT


@pytest.fixture(scope="function")
def mock_fetch_viewers(monkeypatch):
    monkeypatch.setattr(twitch.Game, "fetch_viewers", mock.Mock())


def test_search_games(mock_session, games_search_response, game1json, game2json,
                      mock_fetch_viewers):
    Session.request.return_value = games_search_response
    ks = twitch.KrakenSession()
    games = ks.search_games(query='test', live=True)
    for g, j  in zip(games, [game1json, game2json]):
        conftest.assert_game_equals_json(g, j)
    Session.request.assert_called_with('GET',
                                       twitch.TWITCH_KRAKENURL + 'search/games',
                                       params={'query': 'test',
                                               'type': 'suggest',
                                               'live': True},
                                       allow_redirects=True)


def test_top_games(mock_session, game1json, game2json,
                   top_games_response):
    Session.request.return_value = top_games_response
    ks = twitch.KrakenSession()
    games = ks.top_games(limit=10, offset=0)
    for g, j in zip(games, [game1json, game2json]):
        conftest.assert_game_equals_json(g, j)
    assert games[0].viewers == 123
    assert games[0].channels == 32
    assert games[1].viewers == 7312
    assert games[1].channels == 95
    Session.request.assert_called_with('GET',
                                       twitch.TWITCH_KRAKENURL + 'games/top',
                                       params={'limit': 10,
                                               'offset': 0},
                                       allow_redirects=True)


def test_get_channel(mock_session, get_channel_response, channel1json):
    Session.request.return_value = get_channel_response
    ks = twitch.KrakenSession()
    channel = ks.get_channel(channel1json['name'])

    conftest.assert_channel_equals_json(channel, channel1json)
    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'channels/'+ channel1json['name'],
        allow_redirects=True)


def test_search_channels(mock_session, search_channels_response,
                         channel1json, channel2json):
    Session.request.return_value = search_channels_response
    ks = twitch.KrakenSession()
    channels = ks.search_channels(query='test',
                                  limit=35,
                                  offset=10)

    for c, j in zip(channels, [channel1json, channel2json]):
        conftest.assert_channel_equals_json(c, j)

    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'search/channels',
        params={'query': 'test',
                'limit': 35,
                'offset': 10},
        allow_redirects=True)


def test_get_stream(mock_session, get_stream_response, stream1json):
    Session.request.return_value = get_stream_response
    ks = twitch.KrakenSession()
    s1 = ks.get_stream(stream1json['channel']['name'])
    s2 = ks.get_stream(twitch.Channel.wrap_json(stream1json['channel']))

    for s in [s1, s2]:
        conftest.assert_stream_equals_json(s, stream1json)

    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'streams/' +
        stream1json['channel']['name'],
        allow_redirects=True)


def test_get_streams(mock_session, search_streams_response,
                     stream1json, stream2json, game1json):
    Session.request.return_value = search_streams_response
    ks = twitch.KrakenSession()
    c = twitch.Channel.wrap_json(stream1json['channel'])
    games = [game1json['name'],
             twitch.Game.wrap_json(game1json, viewers=1, channels=1)]
    channels = [[c, 'asdf'], None]
    params = [{'game': game1json['name'],
              'channel': 'test_channel,asdf',
              'limit': 35,
              'offset': 10},
              {'game': game1json['name'],
              'limit': 35,
              'offset': 10}]

    for g, c, p in zip(games, channels, params):
        streams = ks.get_streams(game=g,
                                 channels=c,
                                 limit=35,
                                 offset=10)

        for s, j in zip(streams, [stream1json, stream2json]):
            conftest.assert_stream_equals_json(s, j)

        Session.request.assert_called_with('GET',
            twitch.TWITCH_KRAKENURL + 'streams',
            params=p,
            allow_redirects=True)


def test_search_streams(mock_session, search_streams_response,
                        stream1json, stream2json):
    Session.request.return_value = search_streams_response
    ks = twitch.KrakenSession()
    streams = ks.search_streams(query='testquery',
                                hls=False,
                                limit=25,
                                offset=10)

    for s, j in zip(streams, [stream1json, stream2json]):
        conftest.assert_stream_equals_json(s, j)

    p={'query': 'testquery',
       'hls': False,
       'limit': 25,
       'offset': 10}
    Session.request.assert_called_with('GET',
            twitch.TWITCH_KRAKENURL + 'search/streams',
            params=p,
            allow_redirects=True)


def test_get_user(mock_session, get_user_response,
                  user1json):
    Session.request.return_value = get_user_response
    ks = twitch.KrakenSession()
    user = ks.get_user('nameofuser')

    conftest.assert_user_equals_json(user, user1json)
