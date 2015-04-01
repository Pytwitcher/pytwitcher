import mock
import pytest

from pytwitcher import cache


@pytest.mark.parametrize('interval', [10, 40, 9999])
def test_interval(interval):
    df = cache.DataRefresher(interval)
    assert df.get_interval() == interval
    assert df._timer.interval() == interval


def test_refresh_all_emit(qtbot):
    df = cache.DataRefresher(0)
    with qtbot.waitSignal(df.refresh_all_ended, timeout=10) as endblocker:
        with qtbot.waitSignal(df.refresh_all_started, timeout=10) as startblocker:
            df.refresh_all()
    assert startblocker.signal_triggered, "refresh_all_started signal not emitted"
    assert endblocker.signal_triggered, "refresh_all_ended signal not emitted"


def test_start(qtbot):
    df = cache.DataRefresher(0)
    df._timer.setSingleShot(True)
    with qtbot.waitSignal(df.refresh_all_ended, timeout=10) as endblocker:
        df.start()
    assert endblocker.signal_triggered


def test_stop(qtbot):
    df = cache.DataRefresher(0)
    df._timer.setSingleShot(True)
    with qtbot.waitSignal(df._timer.timeout, timeout=10) as blocker:
        df.start()
        df.stop()
    assert not blocker.signal_triggered


@pytest.mark.parametrize('name', ['all', 'start', 'all_ended', 'all_started'])
def test_add_refresher_nameclash(name):
    df = cache.DataRefresher(0)
    with pytest.raises(ValueError):
        df.add_refresher(name, None)


@pytest.mark.parametrize('name', ['streams', 'games'])
def test_add_refresher(name, qtbot):
    df = cache.DataRefresher(0)

    update = mock.Mock()
    update.side_effect = (0, 1)
    df.add_refresher(name, update)
    assert getattr(df, name) is None
    with qtbot.waitSignal(df.refresh_ended, timeout=10) as endblocker:
        with qtbot.waitSignal(df.refresh_started, timeout=10) as startblocker:
            getattr(df, 'refresh_%s' % name)()
    assert startblocker.signal_triggered, "refresh_started signal not emitted"
    assert endblocker.signal_triggered, "refresh_ended signal not emitted"
    assert getattr(df, name) == 0, 'Value did not refresh'
    with qtbot.waitSignal(df.refresh_ended, timeout=10) as endblocker:
        with qtbot.waitSignal(df.refresh_started, timeout=10) as startblocker:
            getattr(df, 'refresh_%s' % name)()
    assert startblocker.signal_triggered, "refresh_started signal not emitted"
    assert endblocker.signal_triggered, "refresh_ended signal not emitted"
    assert getattr(df, name) == 1, 'Value did not refresh'


def test_refresh_all(qtbot):
    df = cache.DataRefresher(0)
    update = mock.Mock()
    update.side_effect = (0, 1)
    update2 = mock.Mock()
    update2.side_effect = ('a', 'b')
    df.add_refresher('count', update)
    df.add_refresher('abc', update2)
    for i, j in zip((0, 1), ('a', 'b')):
        with qtbot.waitSignal(df.refresh_all_ended, timeout=10) as endallblocker:
            with qtbot.waitSignal(df.refresh_all_started, timeout=10) as startallblocker:
                with qtbot.waitSignal(df.refresh_ended, timeout=10) as endblocker:
                    with qtbot.waitSignal(df.refresh_started, timeout=10) as startblocker:
                        df.refresh_all()
        assert startblocker.signal_triggered, "refresh_started signal not emitted"
        assert endblocker.signal_triggered, "refresh_ended signal not emitted"
        assert startallblocker.signal_triggered, "refresh_all_started signal not emitted"
        assert endallblocker.signal_triggered, "refresh_all_ended signal not emitted"
        assert df.count == i, "Value did not refresh"
        assert df.abc == j, "Value did not refresh"
