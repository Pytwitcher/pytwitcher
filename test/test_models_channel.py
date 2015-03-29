import os

import pytest
from PySide import QtGui

from pytwitcher import models, cache
from pytwitcherapi import models as apimodels

thisdir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='function')
def apichannel1():
    channel = apimodels.Channel(name='test', status='good', displayname='thc',
        game='LoL', twitchid=6312, views=1234, followers=12, url='testurl',
        language='en', broadcaster_language='de', mature=True,
        logo='channellogo.png', banner='channelbanner.png',
        video_banner='channelvideobanner.png', delay=10)
    return channel


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
    l = mockedchannel.logo
    pixmap = QtGui.QPixmap(os.path.join(thisdir, 'channellogo.png'))
    assert pixmap
    assert l.toImage() == pixmap.toImage()


def test_banner(mockedchannel, qtbot):
    l = mockedchannel.banner
    pixmap = QtGui.QPixmap(os.path.join(thisdir, 'channelbanner.png'))
    assert pixmap
    assert l.toImage() == pixmap.toImage()


def test_video_banner(mockedchannel, qtbot):
    l = mockedchannel.video_banner
    pixmap = QtGui.QPixmap(os.path.join(thisdir, 'channelvideobanner.png'))
    assert pixmap
    assert l.toImage() == pixmap.toImage()


def test_from_channel(apichannel1, qtbot):
    c = models.QtChannel.from_channel(None, None, apichannel1)
    assert c.name == apichannel1.name
    assert c.status == apichannel1.status
    assert c.displayname == apichannel1.displayname
    assert c.game == apichannel1.game
    assert c.twitchid == apichannel1.twitchid
    assert c.views == apichannel1.views
    assert c.followers == apichannel1.followers
    assert c.url == apichannel1.url
    assert c.language == apichannel1.language
    assert c.broadcaster_language == apichannel1.broadcaster_language
    assert c.mature == apichannel1.mature
    assert c._logo == apichannel1.logo
    assert c._banner == apichannel1.banner
    assert c._video_banner == apichannel1.video_banner
    assert c.delay == apichannel1.delay
