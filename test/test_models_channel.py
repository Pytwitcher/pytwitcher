import os

import pytest
from PySide import QtGui

from pytwitcher import models, cache

thisdir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="function")
def filledcache(mockedsession, qtbot):
    c = cache.PixmapLoader(mockedsession)
    c['channellogo.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'channellogo.png'))
    c['channelbanner.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'channelbanner.png'))
    c['channelvideobanner.png'] = QtGui.QPixmap(
        os.path.join(thisdir,'channelvideobanner.png'))
    return c


@pytest.fixture(scope='function')
def mockedchannel(mockedsession, filledcache):
    """Return a qtchannel with a already filled cache."""
    logo = 'channellogo.png'
    banner = 'channelbanner.png'
    video_banner = 'channelvideobanner.png'
    c = models.QtChannel(mockedsession, filledcache, 'TestHisChannel',
                         'Playing Stuff', 'THC', 'Stuff', 15123,
                         90000, 12, 'twitch.tv/thc', 'en', 'en',
                         True, logo, banner, video_banner, 10)
    return c


def test_logo(mockedchannel, qtbot):
    print mockedchannel.cache
    print mockedchannel._logo
    l = mockedchannel.logo
    pixmap = QtGui.QPixmap(os.path.join(thisdir, 'channellogo.png'))
    assert l.toImage() == pixmap.toImage()
