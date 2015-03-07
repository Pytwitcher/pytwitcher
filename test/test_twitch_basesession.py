import pytest
import mock
from requests.exceptions import HTTPError
from requests.sessions import Session
from requests.models import Response

from pytwitch import twitch


@pytest.fixture(scope="function")
def mock_session(monkeypatch):
    monkeypatch.setattr(Session, "request", mock.Mock())


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


@pytest.fixture(scope="function",
                params=[400, 499, 500, 599])
def mock_session_error_status(request, mock_session):
    response = Response()
    response.status_code = request.param
    Session.request.return_value = response


def test_raise(mock_session_error_status):
    bs = twitch.BaseSession()
    with pytest.raises(HTTPError):
        bs.request("GET", "test")
