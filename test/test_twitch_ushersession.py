from requests.sessions import Session

from pytwitcher import twitch


def test_request(mock_session):
    ks = twitch.UsherSession()
    url = "hallo"
    ks.request("GET", url)
    Session.request.assert_called_with("GET", twitch.TWITCH_USHERURL + url)
