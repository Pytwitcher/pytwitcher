import logging
import sys
import webbrowser

from PySide import QtGui, QtCore
from easymodel import treemodel
import qmenuview

from pytwitcher import menus, models, player, pool, session, tray, utils


HELP_URL = "http://pytwitcher.readthedocs.org/en/develop/userdoc/index.html"


logging.basicConfig(level=logging.INFO)


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

        Create a :class:`QtGui.QSystemTrayIcon` to quickly access streams.
        For the tray icon to work on Ubuntu, you might have to install the `sni-qt package <https://launchpad.net/sni-qt>`_.

        :raises: None
        """
        super(PyTwitcherApp, self).__init__()
        self.qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
#        self.qapp.setQuitOnLastWindowClosed(False)
        self.qapp.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False)
        self._called_exec = False  # Save, if launch called qapp.exec_ for quit.
        self.pool = pool.MeanThreadPoolExecutor(max_workers=20)
        self.session = session.QtTwitchSession(self.pool)
        """The :class:`session.QtTwitchSession` that is used for all queries."""

        self.mainmenu = menus.MainMenu(self)
        """The pytwicher main :class:`mainmenu.MainMenu`"""
#        self.tray = tray.PytwitcherTray(self.mainmenu)
        """The :class:`tray.PytwitcherTray` that will give quick access to :data:`PyTwitcherApp.mainmenu`."""
        self.mwin = PyTwitcherWin(mainmenu=self.mainmenu)
        self.topgamesmodel = self.create_top_games_model('small', 10, 10)
        self.mwin.set_top_games_model(self.topgamesmodel)
        self.mainmenu.set_top_games_model(self.topgamesmodel)

    def create_top_games_model(self, logosize, maxgames, maxstreams):
        """Create a new treemodel with topgames and topstreams

        :param logosize: the size of the logos. ``small``, ``medium`` or ``large``.
        :type logosize: :class:`str`
        :param maxgames: the maximum number of games
        :type maxgames: :class:`int`
        :param maxstreams: the maximum number of streams
        :type maxstreams: :class:`int`
        :returns: the created logo
        :rtype: None
        :raises: None
        """
        headers = ['Name', 'Viewers', 'Channels', 'Box']
        rootdata = treemodel.ListItemData(headers)
        rootitem = treemodel.TreeItem(rootdata, parent=None)
        topgames = self.session.top_games(limit=maxgames)
        for g in topgames[:maxgames]:
            data = models.GameItemData(g, logosize)
            models.GameItem(data, rootitem, maxstreams=maxstreams)
        return treemodel.TreeModel(rootitem)

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
#        self.tray.show()
        self.mwin.show()
        if exec_ is True:
            self._called_exec = exec_
            return self.qapp.exec_()

    def quit_app(self, ):
        """Quit app.

        Stops data refreshing and hides the tray icon

        :returns: None
        :rtype: None
        :raises: None
        """
        self.pool.shutdown()
#        self.tray.hide()
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


class PyTwitcherWin(QtGui.QMainWindow):
    """The main pytwitcher gui
    """

    def __init__(self, mainmenu):
        """Inizialize a new pytwitcher window

        :param mainmenu: the main menu to use
        :type mainmenu: :class:`QtGui.QMenu`
        :raises: None
        """
        super(PyTwitcherWin, self).__init__(None)
        self.mainmenu = mainmenu
        self.mainmenu.streamsmenu.action_triggered.connect(self.play)
        mb = self.menuBar()
        mb.setNativeMenuBar(False)
        mb.addMenu(self.mainmenu)
        logo = utils.get_logo()
        self.setWindowIcon(logo)

        self.tab_widget = QtGui.QTabWidget()
        self.gameview = QtGui.QTableView()
        self.gameview.setSelectionMode(self.gameview.NoSelection)
        self.gameview.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.gameview.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.channelview = QtGui.QTableView()
        self.channelview.setSelectionMode(self.channelview.NoSelection)
        self.channelview.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.channelview.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.qoview = QtGui.QTableView()
        self.qoview.setSelectionMode(self.qoview.NoSelection)
        self.qoview.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.qoview.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tab_widget.addTab(self.gameview, 'Games')
        self.tab_widget.addTab(self.channelview, 'Channels')
        self.tab_widget.addTab(self.qoview, 'Quality')
        self.player = player.VideoPlayer(self)
        self.tab_widget.addTab(self.player, 'Player')

        self.gameview.clicked.connect(self.setgame)
        self.channelview.clicked.connect(self.setchannel)
        self.qoview.clicked.connect(self.play)
        self.setCentralWidget(self.tab_widget)
        self.resize(600, 400)

    def set_top_games_model(self, model):
        """Set the top games model

        :param model: the model with the top games
        :type model: :class:`QtCore.QAbstractItemModel`
        :returns: None
        :rtype: None
        :raises: None
        """
        self.gameview.setModel(model)

    def setgame(self, index):
        if self.channelview.model() is not index.model():
            self.channelview.setModel(index.model())
        self.channelview.setRootIndex(index)
        self.tab_widget.setCurrentWidget(self.channelview)

    def setchannel(self, index):
        if self.qoview.model() is not index.model():
            self.qoview.setModel(index.model())
        self.qoview.setRootIndex(index)
        self.tab_widget.setCurrentWidget(self.qoview)

    def play(self, index):
        self.tab_widget.setCurrentWidget(self.player)
        quality = index.data(QtCore.Qt.DisplayRole)
        stream = index.parent().data(treemodel.INTERNAL_OBJ_ROLE)
        self.player.play(stream, quality)
