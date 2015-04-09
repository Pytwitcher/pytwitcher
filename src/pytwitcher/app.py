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
        self.session = session.QtTwitchSession()
        self.menu = QtGui.QMenu("Streams")
        self.main = QtGui.QMainWindow()

        self.data = cache.DataRefresher(300000)
        self.data.add_refresher('top_games', self.session.top_games)
        self.data.refresh_ended.connect(self.update_menu)
        self.data.refresh_all()
        self.data.start()
        self.main.menuBar().setNativeMenuBar(False)
        self.main.menuBar().addMenu(self.menu)
        self.main.show()

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
        quali, ok = QtGui.QInputDialog.getItem(self.main, "Choose Quality",
                                               "Quality Options for %s" %
                                               stream.channel.name,
                                               stream.quality_options,
                                               editable=False)
        if ok:
            stream.play(quali)


if __name__ == "__main__":
    qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
    app = PyTwitcherApp()
    sys.exit(qapp.exec_())
