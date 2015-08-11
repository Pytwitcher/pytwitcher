"""Module for the main menu that will be displayed at the top
off the application and as a context menu of the tray icon."""

import logging
import sys
import functools

from PySide import QtGui
import qmenuview

if sys.version_info[0] == 2:
    import futures
else:
    import concurrent.futures as futures

log = logging.getLogger(__name__)


class MainMenu(QtGui.QMenu):
    """The main menu that will be displayed at the top
    off the application and as a context menu of the tray icon"""

    def __init__(self, app, name="Pytwicher"):
        """The name of the main menu

        :param topgamesmodel: the model for the games menu view
        :type topgamesmodel: :class:`QtCore.QAbstractItemModel`
        :param app: the pytwitcher app that needs a main menu
        :type app: :class:`pytwitcher.app.PyTwicherApp`
        :param name: the label text of the menu
        :type name: :class:`str`
        :returns: None
        :rtype: None
        :raises: None
        """
        super(MainMenu, self).__init__(name)
        self.app = app
        """The pytwicherapp that created this menu"""
        self.streamsmenu = None
        """The top games/streams :class:`qmenuview.MenuView`."""
        self.followingmennu = None
        """The streams the user is following :class:`qmenuview.MenuView`."""
        self.helpaction = None
        """The :class:`QtGui.QAction` which triggers
        :meth:`pytwicher.app.PyTwitcherApp.show_help`."""
        self.quitaction = None
        """The :class:`QtGui.QAction` which triggers
        :meth:`pytwitcher.app.PyTwicherApp.quit_app`."""
        self.loginaction = None
        """The :class:`LoginAction` where the user can login."""
        self.add_submenus()
        cb = functools.partial(self.followingmenu.menuAction().setVisible, True)
        self.app.login.connect(cb)

    def setVisible(self, visible):
        """Do not hide!

        :param visible: If True, show the menu
        :type visible: :class:`bool`
        :returns: None
        :rtype: None
        :raises: None
        """
        if visible:
            super(MainMenu, self).setVisible(visible)

    def add_submenus(self, ):
        """Add submenus to the main menu

        :returns: None
        :rtype: None
        :raises: None
        """
        self.streamsmenu = qmenuview.MenuView("Games")
        self.streamsmenu.model = self.app.topgamesmodel
        self.followingmenu = qmenuview.MenuView("Following")
        self.followingmenu.model = self.app.followingmodel
        self.loginaction = LoginAction(self.app, self)
        self.helpaction = QtGui.QAction("Help", self)
        self.helpaction.triggered.connect(self.app.show_help)
        self.quitaction = QtGui.QAction("Quit", self)
        self.quitaction.triggered.connect(self.app.quit_app)

        self.addMenu(self.streamsmenu)
        self.addMenu(self.followingmenu)
        self.followingmenu.menuAction().setVisible(False)
        self.seperator1 = self.addSeparator()
        self.addAction(self.loginaction)
        self.addAction(self.loginaction)
        self.seperator2 = self.addSeparator()
        self.addAction(self.helpaction)
        self.seperator3 = self.addSeparator()
        self.addAction(self.quitaction)


class LoginAction(QtGui.QAction):
    """Login Action"""

    def __init__(self, app, parent=None):
        super(LoginAction, self).__init__("Login", parent)
        self.app = app
        self.app.login.connect(self.login_finished)
        self.triggered.connect(self.login)

    def login(self, ):
        """

        :returns: None
        :rtype: None
        :raises: None
        """
        self.setText("Click when finished.")
        self.triggered.disconnect(self.login)
        self.triggered.connect(self.shutdown)
        self.app.session.start_login_server()
        import webbrowser
        url = self.app.session.get_auth_url()
        webbrowser.open(url)

    def shutdown(self, ):
        """

        :returns: None
        :rtype: None
        :raises: None
        """
        self.triggered.disconnect(self.shutdown)
        self.app.session.shutdown_login_server()
        if self.app.session.authorized:
            self.app.login.emit()
        else:
            self.setText("Login")
            self.triggered.connect(self.login)

    def login_finished(self, ):
        """Set the username

        :returns: None
        :rtype: None
        :raises: None
        """
        name = self.app.session.current_user.name
        self.setText("%s" % name)
