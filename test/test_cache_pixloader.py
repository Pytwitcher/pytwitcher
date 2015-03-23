import pytest
import mock
import requests
from PySide import QtGui

from pytwitcher import cache


@pytest.fixture(scope='function')
def mock_session(monkeypatch):
    """Return a session with request method mocked"""
    s = requests.Session()
    s.request = mock.Mock()
    return s


@pytest.fixture(scope='function')
def pixmap_response():
    """Return a mocked respone that contains a picture as content"""
    m = mock.Mock()
    with open('testsmiley.png', 'r') as f:
        c = f.read()
    m.content = c
    return m


def test_load_picture(mock_session, pixmap_response):
    url = 'testurl'
    mock_session.request.return_value = pixmap_response
    pl = cache.PixmapLoader(mock_session)

    pixmap = pl.load_picture(url)
    assert pixmap == QtGui.QPixmap('testsmiley.png')
