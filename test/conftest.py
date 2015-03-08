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
