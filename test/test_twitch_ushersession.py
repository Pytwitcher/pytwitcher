import m3u8
import mock
import pytest
from requests.sessions import Session

from pytwitcher import twitch


@pytest.fixture(scope='function')
def playlist():
    p =\
"""#EXTM3U
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="chunked",NAME="Source"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="chunked"
sourclink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="high",NAME="High"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="high"
highlink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="medium",NAME="Medium"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="medium"
mediumlink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="low",NAME="Low"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="low"
lowlink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="mobile",NAME="Mobile"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="mobile"
mobilelink
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="audio_only",NAME="Audio Only"
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="audio_only"
audioonlylink"""
    return p


@pytest.fixture(scope='function')
def mock_get_channel_access_token(monkeypatch):
    monkeypatch.setattr(twitch.APISession, 'get_channel_access_token', mock.Mock())


def test_request(mock_session):
    us = twitch.UsherSession()
    url = "hallo"
    us.request("GET", url)
    Session.request.assert_called_with("GET", twitch.TWITCH_USHERURL + url)


def test_get_playlist(mock_session, mock_get_channel_access_token,
                      channel1json, playlist):
    token = 'sometoken'
    sig = 'somesig'
    twitch.APISession.get_channel_access_token.return_value = (token, sig)
    mockresponse = mock.Mock()
    mockresponse.text = playlist
    Session.request.return_value = mockresponse
    us = twitch.UsherSession()
    channels=['test_channel', twitch.Channel.wrap_json(channel1json)]
    params={'token':token,'sig':sig,'allow_audio_only':True,'allow_source_only':True}
    mediaids=['chunked','high','medium','low','mobile','audio_only']
    for c in channels:
        p = us.get_playlist(c)
        for pl, mi in zip(p.playlists,mediaids):
            assert pl.media[0].group_id == mi
        Session.request.assert_called_with('GET',
            twitch.TWITCH_USHERURL + 'channel/hls/test_channel.m3u8',
            params=params, allow_redirects=True)
        twitch.APISession.get_channel_access_token.assert_called_with('test_channel')


@pytest.fixture(scope='function')
def mock_get_playlist(monkeypatch):
    monkeypatch.setattr(twitch.UsherSession, 'get_playlist', mock.Mock())


def test_get_quality_options(mock_get_playlist, playlist, channel1json):
    us = twitch.UsherSession()
    p = m3u8.loads(playlist)
    us.get_playlist.return_value = p
    channels=['test_channel', twitch.Channel.wrap_json(channel1json)]
    for c in channels:
        options = us.get_quality_options(c)
        assert options == ['source', 'high', 'medium', 'low', 'mobile', 'audio']
        us.get_playlist.assert_called_with(c)
