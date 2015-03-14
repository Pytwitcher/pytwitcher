import m3u8
import mock
import pytest

from requests.exceptions import HTTPError
from requests.sessions import Session
from requests.utils import default_headers

from pytwitcher import twitch
from test import conftest


@pytest.fixture(scope="function")
def ts():
    return twitch.TwitchSession()


@pytest.fixture(scope="function")
def mock_fetch_viewers(monkeypatch):
    monkeypatch.setattr(twitch.TwitchSession, "fetch_viewers", mock.Mock())


@pytest.fixture(scope="function")
def mock_session_get_viewers(monkeypatch):
    monkeypatch.setattr(twitch.TwitchSession, "get", mock.Mock())
    mockjson = {"viewers": 124,
                "channels": 12}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = mockjson
    twitch.TwitchSession.get.return_value = mockresponse


@pytest.fixture(scope='function')
def playlist():
    p =\
"""#EXTM3U
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="chunked",NAME="Source"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="chunked"
sourclink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="high",NAME="High"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="high"
highlink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="medium",NAME="Medium"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="medium"
mediumlink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="low",NAME="Low"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="low"
lowlink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="mobile",NAME="Mobile"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="mobile"
mobilelink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="audio_only",NAME="Audio Only"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="audio_only"
audioonlylink"""
    return p


@pytest.fixture(scope='function')
def mock_get_channel_access_token(monkeypatch):
    monkeypatch.setattr(twitch.TwitchSession, 'get_channel_access_token', mock.Mock())


@pytest.fixture(scope='function')
def mock_get_playlist(monkeypatch):
    monkeypatch.setattr(twitch.TwitchSession, 'get_playlist', mock.Mock())


@pytest.mark.parametrize("base,url,full", [
    ("testbase/url/", "hallo", "testbase/url/hallo"),
    ("", "hallo", "hallo"),
    (None, "hallo", "hallo"),
])
def test_request(ts, base, url, full, mock_session):
    ts.baseurl = base
    r = ts.request("GET", url)
    Session.request.assert_called_with("GET", full)
    assert r


def test_request_kraken(ts, mock_session):
    url = "hallo"
    oldbaseurl = 'someurl'
    ts.baseurl = oldbaseurl
    oldheaders = ts.headers
    with twitch.kraken(ts):
        ts.request("GET", url)
        assert ts.headers['Accept'] == twitch.TWITCH_HEADER_ACCEPT
    assert ts.baseurl == oldbaseurl
    assert ts.headers == oldheaders
    Session.request.assert_called_with("GET", twitch.TWITCH_KRAKENURL + url)


def test_request_oldapi(ts, mock_session):
    url = "hallo"
    oldbaseurl = 'someurl'
    ts.baseurl = oldbaseurl
    ts.headers['test'] = 'test'
    with twitch.oldapi(ts):
        ts.request("GET", url)
        assert ts.headers == default_headers()
    assert ts.baseurl == oldbaseurl
    Session.request.assert_called_with("GET", twitch.TWITCH_APIURL + url)


def test_request_usher(ts, mock_session):
    url = "hallo"
    oldbaseurl = 'someurl'
    ts.baseurl = oldbaseurl
    ts.headers['test'] = 'test'
    with twitch.usher(ts):
        ts.request("GET", url)
        assert ts.headers == default_headers()
    assert ts.baseurl == oldbaseurl
    Session.request.assert_called_with("GET", twitch.TWITCH_USHERURL + url)


def test_raise_httperror(ts, mock_session_error_status):
    with pytest.raises(HTTPError):
        ts.request("GET", "test")


def test_search_games(ts, mock_session, games_search_response, game1json, game2json,
                      mock_fetch_viewers):
    Session.request.return_value = games_search_response
    games = ts.search_games(query='test', live=True)

    for g, j  in zip(games, [game1json, game2json]):
        conftest.assert_game_equals_json(g, j)

    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'search/games',
        params={'query': 'test',
                'type': 'suggest',
                'live': True},
        allow_redirects=True)

    ts.fetch_viewers.assert_has_calls([mock.call(g) for g in games],
                                      any_order=True)


def test_fetch_viewers(ts, mock_session_get_viewers):
    game = twitch.Game(name="Test", box={}, logo={}, twitchid=214)
    ts.fetch_viewers(game)
    assert game.viewers == 124
    assert game.channels == 12
    ts.get.assert_called_with("streams/summary", params={"game": "Test"})


def test_top_games(ts, mock_session, game1json, game2json,
                   top_games_response):
    Session.request.return_value = top_games_response
    games = ts.top_games(limit=10, offset=0)
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


def test_get_game(ts, mock_session, mock_fetch_viewers,
                  games_search_response, game2json):
    Session.request.return_value = games_search_response
    g = ts.get_game(game2json['name'])
    conftest.assert_game_equals_json(g, game2json)


def test_get_channel(ts, mock_session, get_channel_response, channel1json):
    Session.request.return_value = get_channel_response
    channel = ts.get_channel(channel1json['name'])

    conftest.assert_channel_equals_json(channel, channel1json)
    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'channels/'+ channel1json['name'],
        allow_redirects=True)


def test_search_channels(ts, mock_session, search_channels_response,
                         channel1json, channel2json):
    Session.request.return_value = search_channels_response
    channels = ts.search_channels(query='test',
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


def test_get_stream(ts, mock_session, get_stream_response, stream1json):
    Session.request.return_value = get_stream_response
    s1 = ts.get_stream(stream1json['channel']['name'])
    s2 = ts.get_stream(twitch.Channel.wrap_json(stream1json['channel']))

    for s in [s1, s2]:
        conftest.assert_stream_equals_json(s, stream1json)

    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'streams/' +
        stream1json['channel']['name'],
        allow_redirects=True)


def test_get_streams(ts, mock_session, search_streams_response,
                     stream1json, stream2json, game1json):
    Session.request.return_value = search_streams_response
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
        streams = ts.get_streams(game=g,
                                 channels=c,
                                 limit=35,
                                 offset=10)

        for s, j in zip(streams, [stream1json, stream2json]):
            conftest.assert_stream_equals_json(s, j)

        Session.request.assert_called_with('GET',
            twitch.TWITCH_KRAKENURL + 'streams',
            params=p,
            allow_redirects=True)


def test_search_streams(ts, mock_session, search_streams_response,
                        stream1json, stream2json):
    Session.request.return_value = search_streams_response
    streams = ts.search_streams(query='testquery',
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


def test_get_user(ts, mock_session, get_user_response,
                  user1json):
    Session.request.return_value = get_user_response
    user = ts.get_user('nameofuser')

    conftest.assert_user_equals_json(user, user1json)


def test_get_channel_access_token(ts, mock_session, channel1json):
    channels = ["test_channel", twitch.Channel.wrap_json(channel1json)]
    mocktoken = {u'token': u'{"channel":"test_channel"}',
                 u'mobile_restricted': False,
                 u'sig': u'f63275898c8aa0b88a6e22acf95088323f006b9d'}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = mocktoken
    Session.request.return_value = mockresponse
    for c in channels:
        token, sig = ts.get_channel_access_token(c)
        Session.request.assert_called_with('GET',
            twitch.TWITCH_APIURL + 'channels/%s/access_token' % channel1json['name'],
            allow_redirects=True)
        assert token == mocktoken['token']
        assert sig == mocktoken['sig']


def test_get_playlist(ts, mock_session, mock_get_channel_access_token,
                      channel1json, playlist):
    token = 'sometoken'
    sig = 'somesig'
    twitch.TwitchSession.get_channel_access_token.return_value = (token, sig)
    mockresponse = mock.Mock()
    mockresponse.text = playlist
    Session.request.return_value = mockresponse
    channels=['test_channel', twitch.Channel.wrap_json(channel1json)]
    params={'token':token,'sig':sig,'allow_audio_only':True,'allow_source_only':True}
    mediaids=['chunked','high','medium','low','mobile','audio_only']
    for c in channels:
        p = ts.get_playlist(c)
        for pl, mi in zip(p.playlists,mediaids):
            assert pl.media[0].group_id == mi
        Session.request.assert_called_with('GET',
            twitch.TWITCH_USHERURL + 'channel/hls/test_channel.m3u8',
            params=params, allow_redirects=True)
        twitch.TwitchSession.get_channel_access_token.assert_called_with('test_channel')


def test_get_quality_options(ts, mock_get_playlist, playlist, channel1json):
    p = m3u8.loads(playlist)
    ts.get_playlist.return_value = p
    channels=['test_channel', twitch.Channel.wrap_json(channel1json)]
    for c in channels:
        options = ts.get_quality_options(c)
        assert options == ['source', 'high', 'medium', 'low', 'mobile', 'audio']
        ts.get_playlist.assert_called_with(c)
