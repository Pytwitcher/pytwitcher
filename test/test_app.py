import mock
import pytest
from PySide import QtCore

from test import conftest
from pytwitcher import app
from pytwitcherapi import session as apisession


@pytest.fixture(scope='function')
def twitcherapp(request, monkeypatch, mockedsession, qtbot, apigame1, apigame2, apistream1, apistream2):
    topgamesmock = mock.Mock()
    topgamesmock.return_value = [apigame1, apigame2]
    getstreamsmock = mock.Mock()
    getstreamsmock.return_value = [apistream1, apistream2]
    monkeypatch.setattr(apisession.TwitchSession, 'top_games', topgamesmock)
    monkeypatch.setattr(apisession.TwitchSession, 'get_streams', getstreamsmock)
    twitcherapp = app.PyTwitcherApp()
    twitcherapp.session = mockedsession
    twitcherapp.showstreammenu = mock.Mock()

    def fin():
        twitcherapp.quit_app()
        tg_meth = apisession.TwitchSession.top_games
        tg_meth.assert_called_with(limit=10, offset=0)
    request.addfinalizer(fin)

    twitcherapp.launch(exec_=False)
    return twitcherapp


@pytest.fixture(scope='function')
def mainactions(twitcherapp):
    return twitcherapp.mainmenu.actions()


@pytest.fixture(scope='function')
def gameactions(mainactions):
    return mainactions[0].menu().actions()


@pytest.fixture(scope='function', params=(0, 1))
def streamactions(gameactions, request):
    i = request.param
    streamactions = gameactions[i].menu().actions()
    return streamactions


def test_trayicon(twitcherapp):
    assert twitcherapp.tray.isVisible(), "TrayIcon was not shown!"
    assert twitcherapp.tray.contextMenu() is twitcherapp.mainmenu, "TrayIcon has wrong menu"
    assert twitcherapp.tray.icon(), "No Logo set!"


def test_mainmenu(mainactions):
    assert len(mainactions) == 2, "There should be an action for streams and quit."
    assert mainactions[0].text() == "Streams", "This should be the stream menu"
    assert mainactions[1].text() == "Quit", "This should be the quit menu"


def test_gamemenu(gameactions):
    assert len(gameactions) == 2, "There should be 2 menues for the 2 top games"
    assert gameactions[0].text() == "test", "This should be the game menu for apigame1"
    assert gameactions[1].text() == "besttest", "This should be the game menu for apigame2"


def test_streammenu(streamactions):
    assert len(streamactions) == 2, "There should be 2 streams for every game"
    assert streamactions[0].text() == "test: good", "This should be the stream menu for apistream1"
    assert streamactions[1].text() == "besttestchannel: cool", "This should be the stream menu for apistream2"


def test_streammenu_triggerd(twitcherapp, streamactions, qtbot, apistream1):
        with qtbot.waitSignal(streamactions[0].triggered, timeout=5000) as blocker:
            streamactions[0].parentWidget().show()
            qtbot.mouseClick(streamactions[0].parentWidget(), QtCore.Qt.LeftButton)
        assert blocker.signal_triggered,\
            "Clicking on Stream did not trigger showstreammenu"
        s = twitcherapp.showstreammenu.call_args[1]['stream']
        conftest.assert_stream_eq_apistream(s, apistream1)
