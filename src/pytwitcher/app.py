import sys
import webbrowser


from PySide import QtGui, QtCore

from pytwitcher import cache, menus, session, tray


HELP_URL = "http://pytwitcher.readthedocs.org/en/develop/userdoc/index.html"


class PyTwitcherApp(object):
    """Application for running Pytwitcher.

    Create an instance and call :meth:`PyTwitcherApp.launch`.
    """

    def __init__(self, ):
        """Initialize a new pytwitcher app.

        Get or create a :class:`QtGui.QApplication`.

        Call :meth:`QtGui.QApplication.setQuitOnLastWindowClosed` with False,
        because we might only run with a TrayIcon. So every Dialog you close could,
        quit the App. This prevents it.

        Create a :class:`cache.DataRefresher` to refresh the top games/streams and followed streams every x min.

        Create a :class:`QtGui.QSystemTrayIcon` to quickly access streams.
        For the tray icon to work on Ubuntu, you might have to install the `sni-qt package <https://launchpad.net/sni-qt>`_.

        :raises: None
        """
        super(PyTwitcherApp, self).__init__()
        self.qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
        self.qapp.setQuitOnLastWindowClosed(False)
        self._called_exec = False  # Save, if launch called qapp.exec_ for quit.

        self.session = session.QtTwitchSession()
        """The :class:`session.QtTwitchSession` that is used for all queries."""
        self.data = cache.DataRefresher(300000)
        """The :class:`cache.DataRefresher` that stores data, which will be periodically updated."""

        self.mainmenu = menus.MainMenu(self)
        """The pytwicher main :class:`mainmenu.MainMenu`"""
        self.tray = tray.PytwitcherTray(self.mainmenu)
        """The :class:`tray.PytwitcherTray` that will give quick access to :data:`PyTwitcherApp.mainmenu`."""
        self.mwin = QtGui.QMainWindow()
        mb = self.mwin.menuBar()
        mb.setNativeMenuBar(False)
        mb.addMenu(self.mainmenu)

    def launch(self, exec_=True):
        """Start app.

        Make the TrayIcon visible and load the data. Start the timer, so the
        data gets periodically refreshed.

        If exec_=True, then this calls :meth:`QtGui.QApplication.exec_`. So it not will return until the QApplication has quit.
        You quit the QApplication by calling :meth:`PyTwitcherApp.quit_app` or click ``Quit`` in the menu.
        If exec_=False, the QApplication is not executed/no event loop is created. So you will not see anything.

        :param exec_: If True, call :meth:`QtGui.QApplication.exec_`
        :type exec_: :class:`bool`
        :returns: If gui True, the return value of :meth:`QtGui.QApplication.exec_`, else None.
        :rtype: None | :class:`int`
        :raises: None
        """
        self.tray.show()
        self.mwin.show()
        self.data.start()
        if exec_ is True:
            # Delay refresh all so the tray icon is shown first
            timer = QtCore.QTimer()
            timer.setSingleShot(True)
            timer.setInterval(100)
            timer.timeout.connect(self.data.refresh_all)
            timer.start()
            self._called_exec = exec_
            return self.qapp.exec_()
        else:
            self.data.refresh_all()
            return

    def quit_app(self, ):
        """Quit app.

        Stops data refreshing and hides the tray icon

        :returns: None
        :rtype: None
        :raises: None
        """
        self.data.stop()
        self.tray.hide()
        if self._called_exec:
            self.qapp.quit()

    def show_help(self, ):
        """Show the help in the webbrowser

        :returns: None
        :rtype: None
        :raises: None
        """
        webbrowser.open(HELP_URL)


def exec_app():
    """Launches the app, and exits, if the app quits.

    :returns: None
    :raises: SystemExit
    """
    app = PyTwitcherApp()
    sys.exit(app.launch(exec_=True))
