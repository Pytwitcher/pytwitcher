import m3u8
import mock
import pytest
from contextlib import contextmanager

from requests.exceptions import HTTPError
from requests.sessions import Session
from requests.utils import default_headers

from pytwitcher import twitch
from test import conftest


@pytest.fixture(scope="function")
def ts(mock_session):
    """Return a :class:`twitch.TwitchSession`
    and mock the request of :class:`Session`
    """
    return twitch.TwitchSession()


@pytest.fixture(scope="function")
def tswithbase(ts):
    """Return a :class:`twitch.TwitchSession` with
    baseurl 'someurl' and {'test': 'test'} in the headers
    """
    ts.baseurl = 'someurl'
    ts.headers['test'] = 'test'
    return ts


@pytest.fixture(scope="function")
def mock_fetch_viewers(monkeypatch):
    """Mock the fetch_viewers method of :class:`twitch.TwitchSession`"""
    monkeypatch.setattr(twitch.TwitchSession, "fetch_viewers", mock.Mock())


@pytest.fixture(scope="function")
def mock_session_get_viewers(monkeypatch):
    """Mock :meth:`twitch.TwitchSession.get` to return the summary
    result for a game
    """
    monkeypatch.setattr(twitch.TwitchSession, "get", mock.Mock())
    mockjson = {"viewers": 124,
                "channels": 12}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = mockjson
    twitch.TwitchSession.get.return_value = mockresponse


@pytest.fixture(scope='function')
def playlist():
    """Return a sample playlist text"""
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
    """Mock :meth:`twitch.TwitchSession.get_channel_access_token`"""
    monkeypatch.setattr(twitch.TwitchSession, 'get_channel_access_token', mock.Mock())


@pytest.fixture(scope='function')
def mock_get_playlist(monkeypatch):
    """Mock :meth:`twitch.TwitchSession.get_playlist`"""
    monkeypatch.setattr(twitch.TwitchSession, 'get_playlist', mock.Mock())


@contextmanager
def check_base_header(session):
    """Contextmanager for checking if the baseurl and headers are the same
    when exiting.
    """
    oldbaseurl = session.baseurl
    oldheaders = session.headers
    yield
    assert session.baseurl == oldbaseurl
    assert session.headers == oldheaders


@pytest.mark.parametrize("base,url,full", [
    ("testbase/url/", "hallo", "testbase/url/hallo"),
    ("", "hallo", "hallo"),
    (None, "hallo", "hallo"),
])
def test_request(ts, base, url, full, mock_session):
    ts.baseurl = base
    r = ts.request("GET", url)
    # check if the session used the full url
    Session.request.assert_called_with("GET", full)
    assert r


def test_request_kraken(tswithbase, mock_session):
    url = "hallo"
    with check_base_header(tswithbase), twitch.kraken(tswithbase):
        tswithbase.request("GET", url)
        # assert we are using the correct headers
        # assert default headers with 'Accept' have been used
        assert 'test' not in tswithbase.headers
        assert tswithbase.headers['Accept'] == twitch.TWITCH_HEADER_ACCEPT
    # assert the kraken url was used 
    Session.request.assert_called_with("GET", twitch.TWITCH_KRAKENURL + url)


def test_request_oldapi(tswithbase, mock_session):
    url = "hallo"
    with check_base_header(tswithbase), twitch.oldapi(tswithbase):
        tswithbase.request("GET", url)
        assert tswithbase.headers == default_headers()
    # assert that the api url as baseurl was used
    Session.request.assert_called_with("GET", twitch.TWITCH_APIURL + url)


def test_request_usher(tswithbase, mock_session):
    url = "hallo"
    with check_base_header(tswithbase), twitch.usher(tswithbase):
        tswithbase.request("GET", url)
        assert tswithbase.headers == default_headers()
    # assert that the usherurl as baseurl was used
    Session.request.assert_called_with("GET", twitch.TWITCH_USHERURL + url)


def test_raise_httperror(ts, mock_session_error_status):
    # assert that responses with error status_codes
    # immediately get raised as errors
    with pytest.raises(HTTPError):
        ts.request("GET", "test")


def test_search_games(ts, games_search_response,
                      game1json, game2json, mock_fetch_viewers):
    Session.request.return_value = games_search_response
    games = ts.search_games(query='test', live=True)

    # check result
    for g, j  in zip(games, [game1json, game2json]):
        conftest.assert_game_equals_json(g, j)

    #check if request was correct
    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'search/games',
        params={'query': 'test',
                'type': 'suggest',
                'live': True},
        allow_redirects=True)

    # check if mocked fetch viewers was called correctly
    ts.fetch_viewers.assert_has_calls([mock.call(g) for g in games],
                                      any_order=True)


def test_fetch_viewers(ts, mock_session_get_viewers):
    game = twitch.Game(name="Test", box={}, logo={}, twitchid=214)
    game2 = ts.fetch_viewers(game)
    # assert that attributes have been set
    assert game.viewers == 124
    assert game.channels == 12
    # assert the game was also returned
    assert game2 is game
    # assert the request was correct
    ts.get.assert_called_with("streams/summary", params={"game": "Test"})


def test_top_games(ts, game1json, game2json,
                   top_games_response):
    Session.request.return_value = top_games_response
    games = ts.top_games(limit=10, offset=0)
    # check result
    for g, j in zip(games, [game1json, game2json]):
        conftest.assert_game_equals_json(g, j)
    # assert the viewers and channels from the response were already set
    assert games[0].viewers == 123
    assert games[0].channels == 32
    assert games[1].viewers == 7312
    assert games[1].channels == 95
    # assert the request was correct
    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'games/top',
        params={'limit': 10,
                'offset': 0},
        allow_redirects=True)


def test_get_game(ts, mock_fetch_viewers,
                  games_search_response, game2json):
    Session.request.return_value = games_search_response
    g = ts.get_game(game2json['name'])
    conftest.assert_game_equals_json(g, game2json)


def test_get_channel(ts, get_channel_response, channel1json):
    Session.request.return_value = get_channel_response
    channel = ts.get_channel(channel1json['name'])

    conftest.assert_channel_equals_json(channel, channel1json)
    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'channels/'+ channel1json['name'],
        allow_redirects=True)


def test_search_channels(ts, search_channels_response,
                         channel1json, channel2json):
    Session.request.return_value = search_channels_response
    channels = ts.search_channels(query='test',
                                  limit=35,
                                  offset=10)

    # check result
    for c, j in zip(channels, [channel1json, channel2json]):
        conftest.assert_channel_equals_json(c, j)

    # assert the request was correct
    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'search/channels',
        params={'query': 'test',
                'limit': 35,
                'offset': 10},
        allow_redirects=True)


def test_get_stream(ts, get_stream_response, stream1json):
    Session.request.return_value = get_stream_response
    s1 = ts.get_stream(stream1json['channel']['name'])
    s2 = ts.get_stream(twitch.Channel.wrap_json(stream1json['channel']))

    # check result
    for s in [s1, s2]:
        conftest.assert_stream_equals_json(s, stream1json)

    # assert the request was correct
    Session.request.assert_called_with('GET',
        twitch.TWITCH_KRAKENURL + 'streams/' +
        stream1json['channel']['name'],
        allow_redirects=True)


def test_get_streams(ts, search_streams_response, channel1,
                     stream1json, stream2json, game1json):
    Session.request.return_value = search_streams_response
    # check with different input types
    games = [game1json['name'],
             twitch.Game.wrap_json(game1json)]
    channels = [[channel1, 'asdf'], None]
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

        # check the result
        for s, j in zip(streams, [stream1json, stream2json]):
            conftest.assert_stream_equals_json(s, j)

        # assert the request was correct
        Session.request.assert_called_with('GET',
            twitch.TWITCH_KRAKENURL + 'streams',
            params=p,
            allow_redirects=True)


def test_search_streams(ts, search_streams_response,
                        stream1json, stream2json):
    Session.request.return_value = search_streams_response
    streams = ts.search_streams(query='testquery',
                                hls=False,
                                limit=25,
                                offset=10)

    # check the result
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


def test_get_user(ts, get_user_response,
                  user1json):
    Session.request.return_value = get_user_response
    user = ts.get_user('nameofuser')

    conftest.assert_user_equals_json(user, user1json)


def test_get_channel_access_token(ts, channel1):
    # test with different input types
    channels = [channel1.name, channel1]
    mocktoken = {u'token': u'{"channel":"test_channel"}',
                 u'mobile_restricted': False,
                 u'sig': u'f63275898c8aa0b88a6e22acf95088323f006b9d'}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = mocktoken
    Session.request.return_value = mockresponse

    for c in channels:
        token, sig = ts.get_channel_access_token(c)
        Session.request.assert_called_with('GET',
            twitch.TWITCH_APIURL + 'channels/%s/access_token' % channel1.name,
            allow_redirects=True)
        assert token == mocktoken['token']
        assert sig == mocktoken['sig']


def test_get_playlist(ts, mock_get_channel_access_token,
                      channel1, playlist):
    token = 'sometoken'
    sig = 'somesig'
    twitch.TwitchSession.get_channel_access_token.return_value = (token, sig)
    mockresponse = mock.Mock()
    mockresponse.text = playlist
    Session.request.return_value = mockresponse
    # test with different input types
    channels=['test_channel', channel1]
    params={'token':token,'sig':sig,
            'allow_audio_only':True,
            'allow_source_only':True}
    # assert the playlist finds these media ids
    mediaids=['chunked','high','medium','low','mobile','audio_only']
    for c in channels:
        p = ts.get_playlist(c)
        for pl, mi in zip(p.playlists,mediaids):
            assert pl.media[0].group_id == mi
        # assert the request was correct
        Session.request.assert_called_with('GET',
            twitch.TWITCH_USHERURL + 'channel/hls/test_channel.m3u8',
            params=params, allow_redirects=True)
        # assert the mocked get_channel_access_token was called correctly
        twitch.TwitchSession.get_channel_access_token.assert_called_with('test_channel')


def test_get_quality_options(ts, mock_get_playlist, playlist, channel1):
    p = m3u8.loads(playlist)
    ts.get_playlist.return_value = p
    channels=['test_channel', channel1]
    for c in channels:
        options = ts.get_quality_options(c)
        assert options == ['source', 'high', 'medium', 'low', 'mobile', 'audio']
        ts.get_playlist.assert_called_with(c)
