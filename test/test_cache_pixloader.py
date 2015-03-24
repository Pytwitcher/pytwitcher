import os

import pytest
import mock
import requests
from PySide import QtGui

from pytwitcher import cache


@pytest.fixture(scope='function')
def testsmiley():
    """Return a pixmap of the testsmiley.png"""
    url = os.path.join(os.path.dirname(__file__), 'testsmiley.png')
    return QtGui.QPixmap(url)


@pytest.fixture(scope='function')
def mock_session(monkeypatch):
    """Return a session with request method mocked"""
    s = requests.Session()
    s.request = mock.Mock()
    return s


@pytest.fixture(scope='function')
def pixmap_response():
    """Return a mocked response that contains a picture as content"""
    m = mock.Mock()
    url = os.path.join(os.path.dirname(__file__), 'testsmiley.png')
    with open(url, 'rb') as f:
        c = f.read()
    m.content = c
    return m


@pytest.fixture(scope='function')
def mock_pixsession(mock_session, pixmap_response):
    """Return a mocked session that returns pixmap_responses"""
    mock_session.request.return_value = pixmap_response
    return mock_session


def test_load_picture(mock_pixsession, testsmiley):
    url = 'testurl'
    pl = cache.PixmapLoader(mock_pixsession)

    pixmap = pl.load_picture(url)
    assert pixmap == testsmiley
    mock_pixsession.request.assert_called_with('GET', url, allow_redirects=True)


def test_get_item(mock_pixsession, testsmiley):
    url = 'testurl'
    pl = cache.PixmapLoader(mock_pixsession)
    assert url not in pl
    p = pl[url]
    assert p == testsmiley
    assert url in pl

    p2 = pl[url]
    assert p2 == testsmiley
    mock_pixsession.request.assert_called_once_with('GET', url, allow_redirects=True)
