import mock
import pytest
from PySide import QtCore

from test import conftest
from pytwitcher import app
from pytwitcherapi import session as apisession


@pytest.fixture(scope='function')
def twitcherapp(monkeypatch, mockedsession, qtbot, apigame1, apigame2, apistream1, apistream2):
    topgamesmock = mock.Mock()
    topgamesmock.return_value = [apigame1, apigame2]
    getstreamsmock = mock.Mock()
    getstreamsmock.return_value = [apistream1, apistream2]
    monkeypatch.setattr(apisession.TwitchSession, 'top_games', topgamesmock)
    monkeypatch.setattr(apisession.TwitchSession, 'get_streams', getstreamsmock)
    twitcherapp = app.PyTwitcherApp()
    twitcherapp.session = mockedsession
    twitcherapp.showstreammenu = mock.Mock()
    return twitcherapp


def test_launch(twitcherapp, qtbot, apistream1):
    twitcherapp.launch(gui=False)
    tg_meth = apisession.TwitchSession.top_games
    tg_meth.assert_called_with(limit=10, offset=0)
    assert twitcherapp.tray.isVisible(), "TrayIcon was not shown!"
    assert twitcherapp.tray.contextMenu() is twitcherapp.mainmenu, "TrayIcon has wrong menu"
    acs = twitcherapp.mainmenu.actions()
    assert len(acs) == 2, "There should be an action for streams and quit."
    assert acs[0].text() == "Streams", "This should be the stream menu"
    assert acs[1].text() == "Quit", "This should be the quit menu"
    gameacs = acs[0].menu().actions()
    assert len(gameacs) == 2, "There should be 2 menues for the 2 top games"
    assert gameacs[0].text() == "test", "This should be the game menu for apigame1"
    assert gameacs[1].text() == "besttest", "This should be the game menu for apigame2"
    for g in gameacs:
        streamacs = g.menu().actions()
        assert len(streamacs) == 2, "There should be 2 streams for every game"
        assert streamacs[0].text() == "test: good", "This should be the stream menu for apistream1"
        assert streamacs[1].text() == "besttestchannel: cool", "This should be the stream menu for apistream2"
        with qtbot.waitSignal(streamacs[0].triggered, timeout=5000) as blocker:
            streamacs[0].parentWidget().show()
            qtbot.mouseClick(streamacs[0].parentWidget(), QtCore.Qt.LeftButton)
        assert blocker.signal_triggered,\
            "Clicking on Stream did not trigger showstreammenu"
        s = twitcherapp.showstreammenu.call_args[1]['stream']
        conftest.assert_stream_eq_apistream(s, apistream1)
    assert twitcherapp.showstreammenu.call_count == 2,\
        "Showstreammenu should have been called 2 times. 1 for each top game."
