import sys
import functools

from PySide import QtGui

from pytwitcher import cache, session


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

        self.session = session.QtTwitchSession()
        """The :class:`session.QtTwitchSession` that is used for all queries."""

        self.mainmenu = QtGui.QMenu("PyTwitcher")
        """The pytwicher main :class:`QtGui.QMenu`"""
        self.topgamesmenu = QtGui.QMenu("Streams")
        """The top games/top stremas :class:`QtGui.QMenu`"""
        self.mainmenu.addMenu(self.topgamesmenu)

        self.quitaction = QtGui.QAction("Quit", self.mainmenu)
        self.quitaction.triggered.connect(self.quit_app)
        self.mainmenu.addAction(self.quitaction)

        self.data = cache.DataRefresher(300000)
        """The :class:`cache.DataRefresher` that stores data, which will be periodically updated."""
        self.data.add_refresher('top_games', self.session.top_games)
        self.data.refresh_ended.connect(self.update_menu)

        self.tray = QtGui.QSystemTrayIcon()
        """The :class:`QtGui.QSystemTrayIcon` that will give quick access to :data:`PyTwitcherApp.mainmenu`."""
        self.tray.setContextMenu(self.mainmenu)

    def launch(self, gui=True):
        """Start app.

        Make the TrayIcon visible and load the data. Start the timer, so the
        data gets periodically refreshed.

        If gui=True, then this calls :meth:`QtGui.QApplication.exec_`. So it not will return until the QApplication has quit.
        You quit the QApplication by calling :meth:`PyTwitcherApp.quit_app` or click ``Quit`` in the menu.
        If gui=False, the QApplication is not executed/no event loop is created. So you will not see anything.

        :param gui: If True, call :meth:`QtGui.QApplication.exec_`
        :type gui: :class:`bool`
        :returns: If gui True, the return value of :meth:`QtGui.QApplication.exec_`, else None.
        :rtype: None | :class:`int`
        :raises: None
        """
        self.data.refresh_all()
        self.data.start()
        self.tray.setVisible(True)
        if gui is True:
            return self.qapp.exec_()
        else:
            return

    def quit_app(self, ):
        """Quit app.

        Calls :meth:`QtGui.QApplication.quit`.

        :returns: None
        :rtype: None
        :raises: None
        """
        self.qapp.quit()

    def update_menu(self, name):
        """Update one of the menues that store data which will periodically update.

        :param name: ``'top_games'`` will update the ``Streams`` menu.
        :type name: :class:`str`
        :returns: None
        :rtype: None
        :raises: None
        """
        if name != 'top_games':
            return
        self.topgamesmenu.clear()
        for g in self.data.top_games:
            m = QtGui.QMenu(g.name, self.topgamesmenu)
            self.topgamesmenu.addMenu(m)
            for s in g.top_streams():
                a = m.addAction("%s: %s" % (s.channel.name, s.channel.status))
                f = functools.partial(self.showstreammenu, stream=s)
                a.triggered.connect(f)

    def showstreammenu(self, stream):
        """Create a dialog that lets the user choose a quality for the stream.

        If the user confirms, the stream is played.

        :param stream: The stream to show
        :type stream: :class:`pytwitcher.models.QtStream`
        :returns: None
        :rtype: None
        :raises: None
        """
        quali, ok = QtGui.QInputDialog.getItem(None, "Choose Quality",
                                               "Quality Options for %s" %
                                               stream.channel.name,
                                               stream.quality_options,
                                               editable=False)
        if ok:
            stream.play(quali)


if __name__ == "__main__":
    app = PyTwitcherApp()
    sys.exit(app.launch(gui=True))
