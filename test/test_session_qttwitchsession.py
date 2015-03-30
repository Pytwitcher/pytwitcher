from test import conftest
from pytwitcher import session


def test_get_streams(mock_get_streams, apistream1):
    apistreams = [apistream1]
    mock_get_streams.get_streams.return_value = apistreams
    qtts = session.QtTwitchSession()
    kwargs = {'game': 'Test', 'channels': ['c1', 'c2'], 'limit': 12, 'offset': 24}
    streams = qtts.get_streams(**kwargs)
    assert streams
    for qts, apis in zip(streams, apistreams):
        conftest.assert_stream_eq_apistream(qts, apis)
        assert qts.session is qtts
        assert qts.cache is qtts.cache
    mock_get_streams.get_streams.assert_called_with(**kwargs)
