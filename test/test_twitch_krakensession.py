from requests.sessions import Session

from pytwitcher import twitch


def test_request(mock_session):
    ks = twitch.KrakenSession()
    url = "hallo"
    ks.request("GET", url)
    Session.request.assert_called_with("GET", twitch.TWITCH_KRAKENURL + url)
    assert ks.headers['Accept'] == twitch.TWITCH_HEADER_ACCEPT
