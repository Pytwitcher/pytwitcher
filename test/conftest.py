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
    return {"name": "Test", "box": {}, "logo": {}, "_id": 1252}


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
