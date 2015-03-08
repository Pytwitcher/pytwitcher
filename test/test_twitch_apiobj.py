import pytest

from pytwitcher import twitch


def test_getitem():
    testdict = {'a': 1, 'b': 2}
    apiobj = twitch.APIObject(json=testdict)
    assert apiobj['a'] == 1
    assert apiobj['b'] == 2
    with pytest.raises(KeyError):
        apiobj['c']
