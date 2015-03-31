import os

import pytest
from PySide import QtGui

from test import conftest
from pytwitcher import models, cache

thisdir = os.path.abspath(os.path.dirname(__file__))


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
def apistreams(apistream1):
    return [apistream1]


@pytest.fixture(scope='function')
def mock_get_streams_game(mock_get_streams, apistreams):
    mock_get_streams.get_streams.return_value = apistreams
    return mock_get_streams


def test_top_streams(mock_get_streams_game, mockedgame, apistreams):
    streams = mockedgame.top_streams(limit=10)
    assert streams
    # test if returned streams are correct
    for qts, apis in zip(streams, apistreams):
        conftest.assert_stream_eq_apistream(qts, apis)
        assert qts.session is mockedgame.session
        assert qts.cache is mockedgame.session.cache
    # test if the function call was correct
    mock_get_streams_game.get_streams.assert_called_with(game=mockedgame, channels=None, limit=10, offset=0)


def test_top_streams_caching(mock_get_streams_game, mockedgame, ):
    streams = mockedgame.top_streams(limit=1)
    streams2 = mockedgame.top_streams(limit=25)
    assert streams == streams2
    assert mock_get_streams_game.get_streams.call_count == 1


def test_top_streams_limit(mock_get_streams_game, mockedgame):
    mockedgame.top_streams(limit=20)
    streams2 = mockedgame.top_streams(limit=0)
    assert streams2 == []
    assert mock_get_streams_game.get_streams.call_count == 1


def test_top_streams_refresh(mock_get_streams_game, mockedgame):
    streams = mockedgame.top_streams(limit=10)
    streams2 = mockedgame.top_streams(limit=20, force_refresh=True)
    assert streams != streams2
    mock_get_streams_game.get_streams.assert_called_with(game=mockedgame, channels=None, limit=20, offset=0)
    assert mock_get_streams_game.get_streams.call_count == 2
