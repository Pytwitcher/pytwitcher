import sys
import functools

from PySide import QtGui

from pytwitcher import cache, session


class PyTwitcherApp(object):
    """
    """

    def __init__(self, ):
        """

        :raises: None
        """
        super(PyTwitcherApp, self).__init__()
        self.qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
        self.qapp.setQuitOnLastWindowClosed(False)
        self.session = session.QtTwitchSession()
        self.mainmenu = QtGui.QMenu("PyTwitcher")
        self.menu = QtGui.QMenu("Streams")
        self.mainmenu.addMenu(self.menu)
        self.quitaction = QtGui.QAction("Quit", self.mainmenu)
        self.quitaction.triggered.connect(self.quit_app)
        self.mainmenu.addAction(self.quitaction)

        self.data = cache.DataRefresher(300000)
        self.data.add_refresher('top_games', self.session.top_games)
        self.data.refresh_ended.connect(self.update_menu)
        # need https://launchpad.net/sni-qt for unity
        self.tray = QtGui.QSystemTrayIcon()
        self.tray.setContextMenu(self.mainmenu)

    def launch(self, gui=True):
        """

        :param gui:
        :type gui:
        :returns: None
        :rtype: None
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
        """

        :returns: None
        :rtype: None
        :raises: None
        """
        self.qapp.quit()

    def update_menu(self, name):
        """

        :param name:
        :type name:
        :returns: None
        :rtype: None
        :raises: None
        """
        if name != 'top_games':
            return
        self.menu.clear()
        for g in self.data.top_games:
            m = QtGui.QMenu(g.name, self.menu)
            self.menu.addMenu(m)
            for s in g.top_streams():
                a = m.addAction("%s: %s" %(s.channel.name, s.channel.status))
                f = functools.partial(self.showstreammenu, stream=s)
                a.triggered.connect(f)

    def showstreammenu(self, stream):
        """

        :param stream:
        :type stream:
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
