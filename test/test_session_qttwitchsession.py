import mock
import pytest

from test import conftest
from pytwitcher import session
from pytwitcherapi import session as apisession


@pytest.fixture(scope='function')
def apigames(apigame1):
    return [apigame1]


@pytest.fixture(scope='function')
def apistreams(apistream1):
    return [apistream1]


def pytest_generate_tests(metafunc):
    argnames = ['method', 'kwargs', 'returnvfixture', 'assertfunc']
    if not set(argnames).issubset(metafunc.funcargnames):
        return
    args = []
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
    metafunc.parametrize(argnames, args)


def test_qtmodels(method, kwargs, returnvfixture, assertfunc,
               monkeypatch, mockedsession, request):
    returnv = request.getfuncargvalue(returnvfixture)
    m = mock.Mock()
    m.return_value = returnv
    monkeypatch.setattr(apisession.TwitchSession, method, m)
    rvalues = getattr(mockedsession, method)(**kwargs)
    assert rvalues
    for qtm, apim in zip(rvalues, returnv):
        assertfunc(qtm, apim)
        assert qtm.session is mockedsession
        assert qtm.cache is mockedsession.cache
    m.assert_called_with(**kwargs)
