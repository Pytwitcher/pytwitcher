import pytest

from pytwitcher import cache


@pytest.mark.parametrize('interval', [10, 40, 9999])
def test_interval(interval):
    df = cache.DataRefresher(interval)
    assert df.get_interval() == interval
    assert df._timer.interval() == interval


def test_refresh_all_emit(qtbot):
    df = cache.DataRefresher(0)
    with qtbot.waitSignal(df.refresh_all_ended, timeout=100) as endblocker:
        with qtbot.waitSignal(df.refresh_all_started, timeout=100) as startblocker:
            df.refresh_all()
    assert startblocker.signal_triggered, 'refresh_all_started signal not emitted'
    assert endblocker.signal_triggered, 'refresh_all_ended signal not emitted'


def test_start(qtbot):
    df = cache.DataRefresher(0)
    df._timer.setSingleShot(True)
    with qtbot.waitSignal(df.refresh_all_ended, timeout=100) as endblocker:
        df.start()
    assert endblocker.signal_triggered


def test_stop(qtbot):
    df = cache.DataRefresher(0)
    df._timer.setSingleShot(True)
    with qtbot.waitSignal(df._timer.timeout, timeout=10) as blocker:
        df.start()
        df.stop()
    assert not blocker.signal_triggered
