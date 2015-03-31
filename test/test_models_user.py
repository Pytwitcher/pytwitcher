import os

import pytest
from PySide import QtGui

from test import conftest
from pytwitcher import models, cache

thisdir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='function')
def filledcache(mockedsession, qtbot):
    c = cache.PixmapLoader(mockedsession)
    c['userlogo.png'] = QtGui.QPixmap(
        os.path.join(thisdir, 'userlogo.png'))
    return c


@pytest.fixture(scope='function')
def mockeduser(mockedsession, filledcache):
    u = models.QtUser(mockedsession, filledcache, 'user',
                      'Michael Santana', 'userlogo.png',
                      77823, 'Imaqtpie', 'dongers')
    return u


def test_get_logo(mockeduser):
    l = mockeduser.logo
    assert l is mockeduser.cache['userlogo.png']


def test_from_user(apiuser1):
    qtuser = models.QtUser.from_user(None, None, apiuser1)
    conftest.assert_user_eq_apiuser(qtuser, apiuser1)
