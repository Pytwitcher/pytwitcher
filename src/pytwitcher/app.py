import logging
import sys
import webbrowser

import requests
from PySide import QtGui, QtCore
from easymodel import treemodel
import qdarkstyle

from pytwitcher import menus, models, pool, session, tray, mainwin


HELP_URL = "http://pytwitcher.readthedocs.org/en/develop/userdoc/index.html"


logging.basicConfig(level=logging.INFO)
rl = logging.getLogger('requests')
rl.setLevel(logging.WARNING)


class PyTwitcherApp(QtCore.QObject):
    """Application for running Pytwitcher.

    Create an instance and call :meth:`PyTwitcherApp.launch`.
    """

    login = QtCore.Signal()
    """User completed the login process."""
    reloadGamesModel = QtCore.Signal(QtCore.QModelIndex)
    """Reload topgames model at the given parent index"""
    reloadFollowModel = QtCore.Signal(QtCore.QModelIndex)
    """Reload following model at the given parent index"""

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
        self.setup_qapp()
        self._called_exec = False  # Save, if launch called qapp.exec_ for quit.
        self.pool = pool.MeanThreadPoolExecutor(max_workers=20)
        self.create_session(50)
        self.logosize = 'small'
        self.maxgames = 5
        self.maxstreams = 10
        self.topgamesmodel = self.create_top_games_model()
        self.followingmodel = self.create_following_model()
        self.mainmenu = menus.MainMenu(self)
        """The pytwicher main :class:`mainmenu.MainMenu`"""
        self.tray = tray.PytwitcherTray(self.mainmenu)
        """The :class:`tray.PytwitcherTray` that will give quick access to :data:`PyTwitcherApp.mainmenu`."""
        self.mwin = mainwin.PyTwitcherWin(self)
        self.login.connect(self.login_finished)
        self.reloadGamesModel.connect(self._reloadGamesModel)
        self.reloadFollowModel.connect(self._reloadFollowModel)

    def setup_qapp(self, ):
        """Setup the QApplication

        :returns: None
        :rtype: None
        :raises: None
        """
        self.qapp = QtGui.QApplication.instance() or QtGui.QApplication([])
        # self.qapp.setQuitOnLastWindowClosed(False)
        self.qapp.setStyleSheet(qdarkstyle.load_stylesheet())
        self.qapp.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False)

    def create_session(self, poolsize):
        """Create a new session and create connectionpools for
        http and https.

        :param poolsize: Number of maximum connections per pool
        :type poolsize: :class:`int`
        :returns: None
        :rtype: None
        :raises: None
        """
        self.session = session.QtTwitchSession(self.pool)
        for mountpoint in ('http://', 'https;//'):
            a = requests.adapters.HTTPAdapter(pool_connections=poolsize, pool_maxsize=poolsize)
            self.session.mount(mountpoint, a)

    def create_top_games_model(self):
        """Create a new treemodel with topgames and topstreams

        :returns: the created treemodel
        :rtype: :class:`treemodel.TreeModel`
        :raises: None
        """
        headers = ['Name', 'Viewers', 'Channels', 'Box']
        rootdata = treemodel.ListItemData(headers)
        rootitem = treemodel.TreeItem(rootdata, parent=None)
        topgames = self.session.top_games(limit=self.maxgames)
        for g in topgames[:self.maxgames]:
            data = models.GameItemData(g, self.logosize)
            models.GameItem(data, rootitem, maxstreams=self.maxstreams)
        return treemodel.TreeModel(rootitem)

    def create_following_model(self,):
        """Create a new treemodel for the following games

        The model is empty until the user logs in.

        :returns: the created treemodel
        :rtype: :class:`treemodel.TreeModel`
        :raises: None
        """
        headers = ['Name', 'Viewers', 'Preview']
        rootdata = treemodel.ListItemData(headers)
        rootitem = treemodel.TreeItem(rootdata, parent=None)
        return treemodel.TreeModel(rootitem)

    def _reloadFollowModel(self, index):
        """Reload the followingmodel at the given parent index

        :param index: the parent index
        :type index: :class:`QtCore.QModelIndex`
        :returns: None
        :rtype: None
        :raises: None
        """
        if index.isValid():
            item = index.data(treemodel.TREEITEM_ROLE)
            item.reload_children()
        else:
            r = self.followingmodel.root
            for c in list(r.childItems):
                r.remove_child(c)
            self.login_finished()

    def _reloadGamesModel(self, index):
        """Reload the topgamesmodel at the given parent index

        :param index: the parent index
        :type index: :class:`QtCore.QModelIndex`
        :returns: None
        :rtype: None
        :raises: None
        """
        if index.isValid():
            item = index.data(treemodel.TREEITEM_ROLE)
            item.reload_children()
        else:
            r = self.topgamesmodel.root
            for c in list(r.childItems):
                r.remove_child(c)
            topgames = self.session.top_games(limit=self.maxgames)
            for g in topgames[:self.maxgames]:
                data = models.GameItemData(g, self.logosize)
                models.GameItem(data, r, maxstreams=self.maxstreams)

    def login_finished(self, ):
        """Load the following streams

        :returns: None
        :rtype: None
        :raises: None
        """
        followed = self.session.followed_streams()
        rootitem = self.followingmodel.root
        for stream in followed:
            data = models.StreamItemData(stream, self.logosize)
            models.StreamItem(data, rootitem)

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
