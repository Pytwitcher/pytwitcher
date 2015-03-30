import os

import mock
import pytest
from PySide import QtGui

from test import conftest
from pytwitcher import models, cache
from pytwitcherapi import models as apimodels
from pytwitcherapi import session as apisession

thisdir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='function')
def apigame1():
    game = apimodels.Game(name='test',
                          box={'small':'testbox'},
                          logo={'medium': 'testlogo'},
                          twitchid=1234,
                          viewers=9999,
                          channels=16)
    return game


@pytest.fixture(scope="function")
def filledcache(mockedsession, qtbot):
    c = cache.PixmapLoader(mockedsession)
    c['smallgamebox.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'smallgamebox.png'))
    c['mediumgamebox.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'mediumgamebox.png'))
    c['largegamebox.png'] = QtGui.QPixmap(
        os.path.join(thisdir,'largegamebox.png'))
    c['smallgamelogo.png'] = QtGui.QPixmap(
        os.path.join(thisdir,'smallgamelogo.png'))
    c['mediumgamelogo.png'] = QtGui.QPixmap(
        os.path.join(thisdir,'mediumgamelogo.png'))
    c['largegamelogo.png'] = QtGui.QPixmap(
        os.path.join(thisdir,'largegamelogo.png'))
    return c


@pytest.fixture(scope='function')
def mockedgame(mockedsession, filledcache):
    """Return a qtgame with a already filled cache."""
    box = {'small': 'smallgamebox.png',
           'medium': 'mediumgamebox.png',
           'large': 'largegamebox.png'}
    logo = {'small': 'smallgamelogo.png',
            'medium': 'mediumgamelogo.png',
            'large': 'largegamelogo.png'}
    g = models.QtGame(mockedsession, filledcache, 'TestGame',
                      box, logo, 424242, 10, 3)
    return g


@pytest.mark.parametrize('size,pixmap', [
    ('small', os.path.join(thisdir,'smallgamebox.png')),
    ('medium', os.path.join(thisdir,'mediumgamebox.png')),
    ('large', os.path.join(thisdir,'largegamebox.png')),
])
def test_get_box(size, pixmap, mockedgame, qtbot):
    b = mockedgame.get_box(size)
    pixmap = QtGui.QPixmap(pixmap)
    assert b and pixmap
    assert b.toImage() == pixmap.toImage()


@pytest.mark.parametrize('size,pixmap', [
    ('small', os.path.join(thisdir,'smallgamelogo.png')),
    ('medium', os.path.join(thisdir,'mediumgamelogo.png')),
    ('large', os.path.join(thisdir,'largegamelogo.png')),
])
def test_get_logo(size, pixmap, mockedgame, qtbot):
    l = mockedgame.get_logo(size)
    pixmap = QtGui.QPixmap(pixmap)
    assert l and pixmap
    assert l.toImage() == pixmap.toImage()


def test_from_game(apigame1):
    qtgame = models.QtGame.from_game(None, None, apigame1)
    assert qtgame.name == apigame1.name
    assert qtgame.box == apigame1.box
    assert qtgame.logo == apigame1.logo
    assert qtgame.twitchid == apigame1.twitchid
    assert qtgame.viewers == apigame1.viewers
    assert qtgame.channels == apigame1.channels


@pytest.fixture(scope='function')
def mock_get_streams(monkeypatch):
    monkeypatch.setattr(apisession.TwitchSession, "get_streams", mock.Mock())
    return apisession.TwitchSession


def test_top_streams(mock_get_streams, mockedgame, apistream1):
    apistreams = [apistream1]
    mock_get_streams.get_streams.return_value = apistreams
    streams = mockedgame.top_streams(limit=10)
    assert streams
    for qts, apis in zip(streams, apistreams):
        conftest.assert_stream_eq_apistream(qts, apis)
        assert qts.session is mockedgame.session
        assert qts.cache is mockedgame.session.cache
    mock_get_streams.get_streams.assert_called_with(game=mockedgame, channels=None, limit=10, offset=0)
