import mock
import pytest

from test import conftest
from pytwitcherapi import session as apisession


@pytest.fixture(scope='function')
def apigames(apigame1):
    return [apigame1]


@pytest.fixture(scope='function')
def apistreams(apistream1):
    return [apistream1]


@pytest.fixture(scope='function')
def apichannels(apichannel1):
    return [apichannel1]


def pytest_generate_tests(metafunc):
    argnames = ['method', 'kwargs', 'returnvfixture', 'assertfunc']
    if metafunc.function.__name__ != 'test_qtmodels':
        return
    args = []
    # for each arg you append you test:
    # 1. a method
    # 2. with the given args
    # 3. whether it returns qtmodels that resemble the given fixture
    # 4. and check it with the given function
    args.append(('search_games',
                 {'query': 'THC', 'live': False},
                 'apigames',
                 conftest.assert_game_eq_apigame))
    args.append(('top_games',
                 {'limit': 20, 'offset': 100},
                 'apigames',
                 conftest.assert_game_eq_apigame))
    args.append(('get_streams',
                 {'game': 'Test', 'channels': ['c1', 'c2'],
                  'limit': 12, 'offset': 24},
                 'apistreams',
                 conftest.assert_stream_eq_apistream))
    args.append(('search_streams',
                 {'query': 'streams?', 'hls': True,
                  'limit': 11, 'offset': 23},
                 'apistreams',
                 conftest.assert_stream_eq_apistream))
    args.append(('search_channels',
                 {'query': 'Haha', 'limit': 12, 'offset': 2},
                 'apichannels',
                 conftest.assert_channel_eq_apichannel))
    metafunc.parametrize(argnames, args)


def test_qtmodels(method, kwargs, returnvfixture, assertfunc,
               monkeypatch, mockedsession, request):
    # return the value of the given fixture for the mock
    returnv = request.getfuncargvalue(returnvfixture)
    m = mock.Mock()
    m.return_value = returnv
    # mock the method on the api class
    monkeypatch.setattr(apisession.TwitchSession, method, m)
    # call the new function which should return qtmodels
    rvalues = getattr(mockedsession, method)(**kwargs)
    # assert that the list is not empty
    assert rvalues
    # for each returned value check if they resemble the one of the fixture
    for qtm, apim in zip(rvalues, returnv):
        # use the assert function
        assertfunc(qtm, apim)
        assert qtm.session is mockedsession
        assert qtm.cache is mockedsession.cache
    # check if the call was made correctly
    m.assert_called_with(**kwargs)
