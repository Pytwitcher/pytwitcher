import mock
import pytest

from requests.sessions import Session
from requests.models import Response


@pytest.fixture(scope="function")
def mock_session(monkeypatch):
    monkeypatch.setattr(Session, "request", mock.Mock())


@pytest.fixture(scope="function",
                params=[400, 499, 500, 599])
def mock_session_error_status(request, mock_session):
    response = Response()
    response.status_code = request.param
    Session.request.return_value = response


@pytest.fixture(scope="function")
def game1json():
    return {"name": "Gaming Talk Shows", "box": {}, "logo": {}, "_id": 1252}


@pytest.fixture(scope="function")
def game2json():
    return {"name": "Test2", "box": {}, "logo": {}, "_id": 1212}


@pytest.fixture(scope="function")
def games_search_response(game1json, game2json):
    searchjson = {"games": [game1json, game2json]}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = searchjson
    return mockresponse


@pytest.fixture(scope="function")
def top_games_response(game1json, game2json):
    topjson = {"top": [{'game': game1json,
                        'viewers': 123,
                        'channels': 32},
                       {'game': game2json,
                        'viewers': 7312,
                        'channels': 95}]}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = topjson
    return mockresponse


def assert_game_equals_json(game, json):
    assert game.name == json["name"]
    assert game.box == json["box"]
    assert game.logo == json["logo"]
    assert game.twitchid == json["_id"]


@pytest.fixture(scope="function")
def channel1json():
    c = {"mature": False,
         "status": "test status",
         "broadcaster_language": "en",
         "display_name": "test_channel",
         "game": "Gaming Talk Shows",
         "delay": 0,
         "language": "en",
         "_id": 12345,
         "name": "test_channel",
         "logo": "test_channel_logo_url",
         "banner": "test_channel_banner_url",
         "video_banner": "test_channel_video_banner_url",
         "url": "http://www.twitch.tv/test_channel",
         "views": 49144894,
         "followers": 215780}
    return c


@pytest.fixture(scope="function")
def channel2json():
    c = {"mature": False,
         "status": "test my status",
         "broadcaster_language": "de",
         "display_name": "huehue",
         "game": "Tetris",
         "delay": 30,
         "language": "kr",
         "_id": 63412,
         "name": "loremipsum",
         "logo": "loremipsum_logo_url",
         "banner": "loremipsum_banner_url",
         "video_banner": "loremipsum_video_banner_url",
         "url": "http://www.twitch.tv/loremipsum",
         "views": 4976,
         "followers": 642}
    return c


@pytest.fixture(scope="function")
def search_channels_response(channel1json, channel2json):
    searchjson = {"channels": [channel1json,
                               channel2json]}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = searchjson
    return mockresponse


@pytest.fixture(scope="function")
def get_channel_response(channel1json):
    mockresponse = mock.Mock()
    mockresponse.json.return_value = channel1json
    return mockresponse


def assert_channel_equals_json(channel, json):
    assert channel.name == json['name']
    assert channel.status == json['status']
    assert channel.displayname == json['display_name']
    assert channel.game == json['game']
    assert channel.twitchid == json['_id']
    assert channel.views == json['views']
    assert channel.followers == json['followers']
    assert channel.url == json['url']
    assert channel.language == json['language']
    assert channel.broadcaster_language == json['broadcaster_language']
    assert channel.mature == json['mature']
    assert channel.logo == json['logo']
    assert channel.banner == json['banner']
    assert channel.video_banner == json['video_banner']
    assert channel.delay == json['delay']


@pytest.fixture(scope="function")
def stream1json(channel1json):
    s = {'game': 'Gaming Talk Shows',
         'viewers': 9865,
         '_id': 34238,
         'preview': {"small": "test_channel-80x45.jpg",
                     "medium": "test_channel-320x180.jpg",
                     "large": "test_channel-640x360.jpg",
                     "template": "test_channel-{width}x{height}.jpg"},
         'channel': channel1json}
    return s


@pytest.fixture(scope="function")
def stream2json(channel2json):
    s = {'game': 'Tetris',
         'viewers': 7563,
         '_id': 145323,
         'preview': {"small": "loremipsum-80x45.jpg",
                     "medium": "loremipsum-320x180.jpg",
                     "large": "loremipsum-640x360.jpg",
                     "template": "loremipsum-{width}x{height}.jpg"},
         'channel': channel2json}
    return s


@pytest.fixture(scope="function")
def search_streams_response(stream1json, stream2json):
    searchjson = {"streams": [stream1json,
                               stream2json]}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = searchjson
    return mockresponse


@pytest.fixture(scope="function")
def get_stream_response(stream1json):
    json = {"stream": stream1json}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = json
    return mockresponse


@pytest.fixture(scope="function")
def get_offline_stream_response():
    mockresponse = mock.Mock()
    mockresponse.json.return_value = {'stream': None}
    return mockresponse


def assert_stream_equals_json(stream, json):
    assert_channel_equals_json(stream.channel, json['channel'])
    assert stream.game == json['game']
    assert stream.viewers == json['viewers']
    assert stream.twitchid == json['_id']
    assert stream.preview == json['preview']


@pytest.fixture(scope="function")
def user1json():
    u = {'type': 'user',
         'name': 'test_user1',
         'logo': 'test_user1_logo.jpeg',
         '_id': 21229404,
         'display_name': 'test_user1',
         'bio': 'test bio woo I am a test user'}
    return u


@pytest.fixture(scope="function")
def get_user_response(user1json):
    mockresponse = mock.Mock()
    mockresponse.json.return_value = user1json
    return mockresponse


def assert_user_equals_json(user, json):
    assert user.usertype == json['type']
    assert user.name == json['name']
    assert user.logo == json['logo']
    assert user.twitchid == json['_id']
    assert user.displayname == json['display_name']
    assert user.bio == json['bio']