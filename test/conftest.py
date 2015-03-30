import os

import mock
import pytest
from PySide import QtGui

from pytwitcher import models, cache, session
from pytwitcherapi import models as apimodels
from pytwitcherapi import session as apisession

thisdir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="function")
def mockedsession():
    s = session.QtTwitchSession()
    s.request = mock.Mock()
    return s


@pytest.fixture(scope='function')
def apigame1():
    game = apimodels.Game(name='test',
                          box={'small':'testbox'},
                          logo={'medium': 'testlogo'},
                          twitchid=1234,
                          viewers=9999,
                          channels=16)
    return game


@pytest.fixture(scope='function')
def apichannel1():
    channel = apimodels.Channel(name='test', status='good', displayname='thc',
        game='LoL', twitchid=6312, views=1234, followers=12, url='testurl',
        language='en', broadcaster_language='de', mature=True,
        logo='channellogo.png', banner='channelbanner.png',
        video_banner='channelvideobanner.png', delay=10)
    return channel


@pytest.fixture(scope='function')
def apistream1(apichannel1):
    preview = {'small': 'smallstreampreview.png',
               'medium': 'mediumstreampreview.png',
               'large': 'largestreampreview.png'}
    stream = apimodels.Stream(game='test', channel=apichannel1, twitchid=6312,
                              viewers=1234, preview=preview)
    return stream


@pytest.fixture(scope="function")
def filledchannelcache(mockedsession, qtbot):
    c = cache.PixmapLoader(mockedsession)
    c['channellogo.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'channellogo.png'))
    c['channelbanner.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'channelbanner.png'))
    c['channelvideobanner.png'] = QtGui.QPixmap(
        os.path.join(thisdir,'channelvideobanner.png'))
    return c


@pytest.fixture(scope='function')
def mockedchannel(mockedsession, filledchannelcache):
    """Return a qtchannel with a already filled cache."""
    logo = 'channellogo.png'
    banner = 'channelbanner.png'
    video_banner = 'channelvideobanner.png'
    c = models.QtChannel(mockedsession, filledchannelcache,
                         'TestHisChannel', 'Playing Stuff', 'THC',
                         'Stuff', 15123, 90000, 12, 'twitch.tv/thc',
                         'en', 'en', True, logo, banner, video_banner, 10)
    return c


def assert_game_eq_apigame(game, apigame):
    assert isinstance(game, models.QtGame)
    assert game.name == apigame.name
    assert game.box == apigame.box
    assert game.logo == apigame.logo
    assert game.twitchid == apigame.twitchid
    assert game.viewers == apigame.viewers
    assert game.channels == apigame.channels


def assert_channel_eq_apichannel(channel, apichannel):
    assert isinstance(channel, models.QtChannel)
    assert channel.name == apichannel.name
    assert channel.status == apichannel.status
    assert channel.displayname == apichannel.displayname
    assert channel.game == apichannel.game
    assert channel.twitchid == apichannel.twitchid
    assert channel.views == apichannel.views
    assert channel.followers == apichannel.followers
    assert channel.url == apichannel.url
    assert channel.language == apichannel.language
    assert channel.broadcaster_language == apichannel.broadcaster_language
    assert channel.mature == apichannel.mature
    assert channel._logo == apichannel.logo
    assert channel._banner == apichannel.banner
    assert channel._video_banner == apichannel.video_banner
    assert channel.delay == apichannel.delay


def assert_stream_eq_apistream(stream, apistream):
    assert isinstance(stream, models.QtStream)
    assert stream.game == apistream.game
    assert isinstance(stream.channel, models.QtChannel)
    assert stream.twitchid == apistream.twitchid
    assert stream.viewers == apistream.viewers
    assert stream.preview == apistream.preview
    assert_channel_eq_apichannel(stream.channel, apistream.channel)


def assert_user_eq_apiuser(user, apiuser):
    assert isinstance(user, models.QtUser)
    assert user.usertype == apiuser.usertype
    assert user.name == apiuser.name
    assert user.logo == apiuser.logo
    assert user.twitchid == apiuser.twitchid
    assert user.displayname == apiuser.displayname
    assert user.bio == apiuser.bio


@pytest.fixture(scope='function')
def mock_get_streams(monkeypatch):
    monkeypatch.setattr(apisession.TwitchSession, "get_streams", mock.Mock())
    return apisession.TwitchSession
