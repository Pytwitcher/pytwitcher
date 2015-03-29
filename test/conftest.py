import mock
import pytest

from pytwitcherapi import session


@pytest.fixture(scope="function")
def mockedsession():
    s = session.TwitchSession()
    s.request = mock.Mock()
    return s
