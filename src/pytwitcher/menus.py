"""Module for the main menu that will be displayed at the top
off the application and as a context menu of the tray icon."""

import logging
import sys
import weakref
import functools

from PySide import QtGui
import qmenuview

if sys.version_info[0] == 2:
    import futures
else:
    import concurrent.futures as futures

log = logging.getLogger(__name__)


class NoHideMenu(QtGui.QMenu):
    """This menu can contain actions which are triggered
     but do not close the menu.

    Use :meth:`NoHideMenu.add_nohide_action` for this feature.

    .. Important:: The references to the added actions are weak.
                   So make sure to reference them somewhere else.

    """

    def __init__(self, *args, **kwargs):
        """Initialize a new menu.

        Use the usual menu arguments.

        :raises: None
        """
        super(NoHideMenu, self).__init__(*args, **kwargs)
        self._nohide_actions = weakref.WeakSet([])

    def add_nohide_action(self, action):
        """Menu will not get hidden if the action is triggered.

        :param action: the action which should not trigger hide
        :type action: :class:`QtGui.QAction`
        :returns: None
        :rtype: None
        :raises: None
        """
        self._nohide_actions.add(action)

    def remove_nohide_action(self, action):
        """Remove the given action so it will hide when triggered

        :param action:the action wich should trigger hide
        :type action: :class:`QtGui.QAction`
        :returns: None
        :rtype: None
        :raises: None
        """
        try:
            self._nohide_actions.remove(action)
        except KeyError:
            pass

    def mouseReleaseEvent(self, e):
        action = self.activeAction()
        if action and action.isEnabled() and not action.menu() and action in self._nohide_actions:
            action.setEnabled(False)
            super(NoHideMenu, self).mouseReleaseEvent(e)
            action.setEnabled(True)
            action.trigger()
        else:
            super(NoHideMenu, self).mouseReleaseEvent(e)


class MainMenu(NoHideMenu):
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
        self.add_nohide_action(self.loginaction)
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
        self.setText("Please log in the browser. Click when finished.")
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
