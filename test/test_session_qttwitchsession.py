import functools

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


def assertlist(qtmodels, apimodels, assertfunc):
    for qtm, apim in zip(qtmodels, apimodels):
        # use the assert function
        assertfunc(qtm, apim)


def assertsingle(qtmodel, apimodel, assertfunc):
    assertfunc(qtmodel, apimodel)


def pytest_generate_tests(metafunc):
    # only generate tests for test_qtmodels
    if metafunc.function.__name__ != 'test_qtmodels':
        return
    argnames = ['method', 'kwargs', 'returnvfixture', 'assertfunc']
    p = functools.partial
    assertlistgame = p(assertlist, assertfunc=
                       conftest.assert_game_eq_apigame)
    assertliststream = p(assertlist, assertfunc=
                         conftest.assert_stream_eq_apistream)
    assertlistchannel = p(assertlist, assertfunc=
                          conftest.assert_channel_eq_apichannel)
    assertsinglegame = p(assertsingle, assertfunc=
                         conftest.assert_game_eq_apigame)
    assertsinglestream = p(assertsingle, assertfunc=
                           conftest.assert_stream_eq_apistream)
    assertsinglechannel = p(assertsingle, assertfunc=
                            conftest.assert_channel_eq_apichannel)
    assertsingleuser = p(assertsingle, assertfunc=
                         conftest.assert_user_eq_apiuser)
    args = []
    # for each arg you append you test:
    # 1. a method
    # 2. with the given args
    # 3. whether it returns qtmodels that resemble the given fixture
    # 4. and check it with the given function
    args.append(('search_games',
                 {'query': 'THC', 'live': False},
                 'apigames',
                 assertlistgame))
    args.append(('top_games',
                 {'limit': 20, 'offset': 100},
                 'apigames',
                 assertlistgame))
    args.append(('get_streams',
                 {'game': 'Test', 'channels': ['c1', 'c2'],
                  'limit': 12, 'offset': 24},
                 'apistreams',
                 assertliststream))
    args.append(('search_streams',
                 {'query': 'streams?', 'hls': True,
                  'limit': 11, 'offset': 23},
                 'apistreams',
                 assertliststream))
    args.append(('search_channels',
                 {'query': 'Haha', 'limit': 12, 'offset': 2},
                 'apichannels',
                 assertlistchannel))
    args.append(('get_game',
                 {'name': 'somegame'},
                 'apigame1',
                 assertsinglegame))
    args.append(('get_channel',
                 {'name': 'somechannel'},
                 'apichannel1',
                 assertsinglechannel))
    args.append(('get_stream',
                 {'name': 'somestream'},
                 'apistream1',
                 assertsinglestream))
    args.append(('get_user',
                 {'name': 'someuser'},
                 'apiuser1',
                 assertsingleuser))

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
    assertfunc(rvalues, returnv)
    # check if the call was made correctly
    m.assert_called_with(**kwargs)
