import mock
import pytest

from requests.sessions import Session
from requests.models import Response


@pytest.fixture(scope="function")
def mock_session(monkeypatch):
    monkeypatch.setattr(Session, "request", mock.Mock())


@pytest.fixture(scope="function",
                params=[400, 499, 500, 599])
def mock_session_error_status(request, mock_session):
    response = Response()
    response.status_code = request.param
    Session.request.return_value = response
