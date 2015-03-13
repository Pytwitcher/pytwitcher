import mock
from requests.sessions import Session

from pytwitcher import twitch


def test_request(mock_session):
    ks = twitch.APISession()
    url = "hallo"
    ks.request("GET", url)
    Session.request.assert_called_with("GET", twitch.TWITCH_APIURL + url)


def test_get_channel_access_token(mock_session, channel1json):
    channels = ["test_channel", twitch.Channel.wrap_json(channel1json)]
    mocktoken = {u'token': u'{"channel":"test_channel"}',
                 u'mobile_restricted': False,
                 u'sig': u'f63275898c8aa0b88a6e22acf95088323f006b9d'}
    mockresponse = mock.Mock()
    mockresponse.json.return_value = mocktoken
    Session.request.return_value = mockresponse
    apis = twitch.APISession()
    for c in channels:
        token, sig = apis.get_channel_access_token(c)
        Session.request.assert_called_with('GET',
            twitch.TWITCH_APIURL + 'channels/%s/access_token' % channel1json['name'],
            allow_redirects=True)
        assert token == mocktoken['token']
        assert sig == mocktoken['sig']
