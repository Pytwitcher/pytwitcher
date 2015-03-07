from pytwitch import twitch
from requests.sessions import Session


def test_request(mock_session):
    ts = twitch.TwitchSession()
    url = "hallo"
    ts.request("GET", url)
    Session.request.assert_called_with("GET", twitch.TWITCH_BASEURL + url)
    assert ts.headers['Accept'] == twitch.TWITCH_HEADER_ACCEPT
