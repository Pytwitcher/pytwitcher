import mock
import pytest

from pytwitcher import twitch


@pytest.fixture(scope="function")
def mock_session_get_viewers(monkeypatch):
    monkeypatch.setattr(twitch.BaseSession, "get", mock.Mock())
    mockjson = {"viewers": 124,
                "channels": 12}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = mockjson
    twitch.BaseSession.get.return_value = mockresponse


def test_game_fetch_viewers(mock_session_get_viewers):
    bs = twitch.BaseSession()
    game = twitch.Game(name="Test", box={}, logo={}, twitchid=214)
    assert game.viewers == 124
    assert game.channels == 12
    bs.get.assert_called_with("streams/summary", params={"game": "Test"})


@pytest.fixture(scope="function")
def game1json():
    return {"name": "Test", "box": {}, "logo": {}, "_id": 1252}


@pytest.fixture(scope="function")
def game2json():
    return {"name": "Test2", "box": {}, "logo": {}, "_id": 1212}


def assert_game_equals_json(game, json):
    assert game.name == json["name"]
    assert game.box == json["box"]
    assert game.logo == json["logo"]
    assert game.twitchid == json["_id"]


def test_wrap_json(game1json, mock_session_get_viewers):
    g = twitch.Game.wrap_json(game1json)
    assert_game_equals_json(g, game1json)


def test_wrap_search(game1json, game2json, mock_session_get_viewers):
    searchjson = {"games": [game1json, game2json]}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = searchjson
    games = twitch.Game.wrap_search(mockresponse)
    for g, j  in zip(games, [game1json, game2json]):
        assert_game_equals_json(g, j)


def test_wrap_topgames(game1json, game2json):
    topjson = {"top": [{"game": game1json, "viewers": 123, "channels": 10},
                       {"game": game2json, "viewers": 543, "channels": 42}]}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = topjson
    games = twitch.Game.wrap_topgames(mockresponse)
    for g, j in zip(games, [game1json, game2json]):
        assert_game_equals_json(g, j)
    assert games[0].viewers == 123
    assert games[0].channels == 10
    assert games[1].viewers == 543
    assert games[1].channels == 42
