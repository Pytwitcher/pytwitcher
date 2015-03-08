import mock
import pytest

from pytwitcher import twitch


@pytest.fixture(scope="function")
def mock_session(monkeypatch):
    monkeypatch.setattr(twitch.BaseSession, "get", mock.Mock())


def test_game_fetch_viewers(mock_session):
    bs = twitch.BaseSession()
    mockjson = {"viewers": 124,
                "channels": 12}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = mockjson
    bs.get.return_value = mockresponse

    game = twitch.Game(name="Test", box={}, logo={}, twitchid=214)
    assert game.viewers == 124
    assert game.channels == 12
    bs.get.assert_called_with("streams/summary", params={"game": "Test"})
