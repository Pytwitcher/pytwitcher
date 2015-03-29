import os

from PySide import QtGui

from test import conftest
from pytwitcher import models

thisdir = os.path.abspath(os.path.dirname(__file__))


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
    conftest.assert_channel_eq_apichannel(c, apichannel1)
