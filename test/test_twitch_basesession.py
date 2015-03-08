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


def test_raise(mock_session_error_status):
    bs = twitch.BaseSession()
    with pytest.raises(HTTPError):
        bs.request("GET", "test")
