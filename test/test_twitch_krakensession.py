import pytest
import mock
from requests.sessions import Session

from pytwitcher import twitch
from conftest import assert_game_equals_json


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
        assert_game_equals_json(g, j)
    Session.request.assert_called_with('GET',
                                       twitch.TWITCH_KRAKENURL + 'search/games',
                                       params={'query': 'test',
                                               'type': 'suggests',
                                               'live': True},
                                       allow_redirects=True)
