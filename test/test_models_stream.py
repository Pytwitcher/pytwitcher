import os
import subprocess

import pytest
import mock
from PySide import QtGui

from test import conftest
from pytwitcher import models, cache

thisdir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="function")
def filledcache(mockedsession, qtbot):
    c = cache.PixmapLoader(mockedsession)
    c['smallstreampreview.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'smallstreampreview.png'))
    c['mediumstreampreview.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'mediumstreampreview.png'))
    c['largestreampreview.png'] = QtGui.QPixmap(
        os.path.join(thisdir,'largestreampreview.png'))
    return c


@pytest.fixture(scope='function')
def mockedstream(mockedsession, filledcache, mockedchannel):
    """Return a qtstream with a already filled cache."""
    preview = {'small': 'smallstreampreview.png',
               'medium': 'mediumstreampreview.png',
               'large': 'largestreampreview.png'}
    s = models.QtStream(mockedsession, filledcache, 'LoL',
                        mockedchannel, 12431, 81, preview)
    return s


@pytest.mark.parametrize('size,pixmap', [
    ('small', os.path.join(thisdir,'smallstreampreview.png')),
    ('medium', os.path.join(thisdir,'mediumstreampreview.png')),
    ('large', os.path.join(thisdir,'largestreampreview.png')),
])
def test_get_preview(size, pixmap, mockedstream, qtbot):
    prev = mockedstream.get_preview(size)
    pixmap = QtGui.QPixmap(pixmap)
    assert prev and pixmap
    assert prev.toImage() == pixmap.toImage()


def test_from_stream(apistream1, apichannel1, qtbot):
    s = models.QtStream.from_stream(None, None, apistream1)
    conftest.assert_stream_eq_apistream(s, apistream1)


@pytest.fixture(scope='function')
def mockedstreamoptions(mockedstream):
    s = mockedstream.session
    s.get_quality_options = mock.Mock()
    options = ['high', 'medium', 'low']
    s.get_quality_options.return_value = options
    return mockedstream


def test_quality_options(mockedstreamoptions):
    options = ['high', 'medium', 'low']
    o = mockedstreamoptions.quality_options
    assert o == options
    s = mockedstreamoptions.session
    s.get_quality_options.assert_called_only_once_with(mockedstreamoptions.channel)
    # test caching
    o2 = mockedstreamoptions.quality_options
    assert o2 == options == o
    assert s.get_quality_options.call_count == 1


@pytest.fixture(scope='function')
def mockpopen(monkeypatch):
    monkeypatch.setattr(subprocess, 'Popen', mock.Mock())
    return subprocess.Popen


@pytest.mark.parametrize('quali,expected', [
    (None, 'high'),
    ('high', 'high'),
    ('medium', 'medium'),
    ('small', 'small')])
def test_play(quali, expected, mockedstreamoptions, mockpopen):
    p = mockedstreamoptions.play(quali)
    assert isinstance(p, mock.Mock)
    mockpopen.assert_called_with(['livestreamer', 'twitch.tv/thc', expected])
