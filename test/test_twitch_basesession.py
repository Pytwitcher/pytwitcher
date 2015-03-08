import pytest

from requests.exceptions import HTTPError
from requests.sessions import Session

from pytwitcher import twitch


@pytest.mark.parametrize("base,url,full", [
    ("testbase/url/", "hallo", "testbase/url/hallo"),
    ("", "hallo", "hallo"),
    (None, "hallo", "hallo"),
])
def test_request(base, url, full, mock_session):
    bs = twitch.BaseSession(base)
    r = bs.request("GET", url)
    Session.request.assert_called_with("GET", full)
    assert r


def test_raise_httperror(mock_session_error_status):
    bs = twitch.BaseSession()
    with pytest.raises(HTTPError):
        bs.request("GET", "test")


def test_get_instance():
    class SubSession(twitch.BaseSession):
        pass

    bs = twitch.BaseSession.get_instance()
    bs2 = twitch.BaseSession.get_instance()
    assert bs is bs2

    ss = SubSession.get_instance()
    assert ss is not bs
    delattr(twitch.BaseSession, "_instance")
    delattr(SubSession, "_instance")
    ss = SubSession.get_instance()
    bs = twitch.BaseSession.get_instance()
    assert ss is not bs
