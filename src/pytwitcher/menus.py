"""Module for the main menu that will be displayed at the top
off the application and as a context menu of the tray icon."""

import logging
import sys
import weakref

from PySide import QtGui, QtCore

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


class LazyMenu(NoHideMenu):
    """Menu which emits the menu action the first time
    it is clicked on.

    Call :meth:`LazyMenu.start_loading` manually.
    """

    loadingfinished = QtCore.Signal(futures.Future)

    def __init__(self, app, *args, **kwargs):
        """Initialize a new LazyMenu"""
        super(LazyMenu, self).__init__(*args, **kwargs)
        self.reloadaction = None
        self.app = app
        self._activated = False
        self.loadingfinished.connect(
            self._receive_data, type=QtCore.Qt.QueuedConnection)

    def start_loading(self,):
        """Submit :meth:`LazyMenu.load_data` to the thread pool.

        Clears the menu and adds an "Loading" action.

        :returns: None
        :raises: None
        """
        future = self.app.pool.submit(self.load_data)
        future.add_done_callback(self.loadingfinished.emit)
        self.clear()
        self.addAction("Loading...")

    def load_data(self, ):
        """This function gets called in another thread and should return data for
        :meth:`LazyMenu.create_submenus`.

        Override this function.

        :returns: Data for submenus
        :raises: None
        """
        pass

    def _receive_data(self, future):
        """Collect the data from future, call :meth:`LazyMenu.create_submenus`.

        If an exception was thrown, create an error menu.

        :param future: the future from :meth:`LazyMenu.start_loading`
        :type future: :class:`concurrent.futures.Future`
        :returns: None
        :rtype: None
        :raises: None
        """
        self.clear()
        self.reloadaction = None
        try:
            result = future.result()
        except:
            log.exception('Error receiving data for menu %s' % self)
            a = self.addAction('Error! Click to try again.')
            a.triggered.connect(self.start_loading)
        else:
            self.create_submenus(result)
            self.addSeparator()
            self.reloadaction = QtGui.QAction("Reload", self)
            self.reloadaction.triggered.connect(self.start_loading)
            self.addAction(self.reloadaction)
            self.add_nohide_action(self.reloadaction)

    def create_submenus(self, data):
        """Create submenus from the data received by the lazy loading

        Override this function!

        :param data: the data returned from :meth:`LazyMenu.load_data`
        :returns: None
        :rtype: None
        :raises: None
        """
        pass


class IconLazyMenu(LazyMenu):
    """LazyMenu which loads its icon in a seperate thread
    """

    iconloaded = QtCore.Signal(futures.Future)

    def __init__(self, app, *args, **kwargs):
        """Initialize a new IconLazyMenu

        :raises: None
        """
        super(IconLazyMenu, self).__init__(app, *args, **kwargs)
        self.iconloaded.connect(
            self._receive_icon, type=QtCore.Qt.QueuedConnection)

    def start_icon_loading(self,):
        """Submit :meth:`LazyMenu.load_icon` to the thread pool.

        :returns: None
        :raises: None
        """
        future = self.app.pool.submit(self.load_icon)
        future.add_done_callback(self.iconloaded.emit)

    def _receive_icon(self, future):
        """Collect the data from future, call :meth:`LazyMenu.create_icon`.

        Sets the icon afterwards.

        :param future: the future from :meth:`LazyMenu.start_icon_loading`
        :type future: :class:`concurrent.futures.Future`
        :returns: None
        :rtype: None
        :raises: None
        """
        try:
            result = future.result()
        except:
            return
        icon = self.create_icon(result)
        if icon:
            self.setIcon(icon)

    def load_icon(self, ):
        """This function gets called in another thread and should return data for
        :meth:`LazyMenu.create_icon`.

        Override this function.

        :returns: data for icon
        :raises: None
        """
        pass

    def create_icon(self, data):
        """Create and return icon from the data received by the lazy loading

        Override this function!

        :param data: the data returned from :meth:`LazyMenu.load_icon`
        :returns: the created icon
        :rtype: :class:`QtGui.QIcon`
        :raises: None
        """
        pass


class MainMenu(NoHideMenu):
    """The main menu that will be displayed at the top
    off the application and as a context menu of the tray icon"""

    def __init__(self, app, name="Pytwicher"):
        """The name of the main menu

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
        """The top games/streams :class:`StreamsMenu`."""
        self.helpaction = None
        """The :class:`QtGui.QAction` which triggers
        :meth:`pytwicher.app.PyTwitcherApp.show_help`."""
        self.quitaction = None
        """The :class:`QtGui.QAction` which triggers
        :meth:`pytwitcher.app.PyTwicherApp.quit_app`."""
        self.loginaction = None
        """The :class:`LoginAction` where the user can login."""

        self.add_submenus()

    def add_submenus(self, ):
        """Add submenus to the main menu

        :returns: None
        :rtype: None
        :raises: None
        """
        self.streamsmenu = StreamsMenu(self.app)
        self.loginaction = LoginAction(self.app, self)
        self.helpaction = QtGui.QAction("Help", self)
        self.helpaction.triggered.connect(self.app.show_help)
        self.quitaction = QtGui.QAction("Quit", self)
        self.quitaction.triggered.connect(self.app.quit_app)

        self.addMenu(self.streamsmenu)
        self.seperator1 = self.addSeparator()
        self.addAction(self.loginaction)
        self.add_nohide_action(self.loginaction)
        self.seperator2 = self.addSeparator()
        self.addAction(self.helpaction)
        self.seperator3 = self.addSeparator()
        self.addAction(self.quitaction)


class StreamsMenu(LazyMenu):
    """Menu with top games which updates itself periodically
    """

    def __init__(self, app, label="Games"):
        """Initialize the streams menu

        Setup data refreshing.

        :param app: the pytwitcher app
        :type app: :class:`pytwitcher.app.PyTwicherApp`
        :param label: the label of the menu
        :type label: :class:`str`
        :raises: None
        """
        super(StreamsMenu, self).__init__(app, label)
        """The pytwicherapp that created this menu"""
        self.start_loading()

    def load_data(self, ):
        """Return data for submenus

        :returns: The topgames
        :rtype: :class:`list` of :class:`pytwitcher.models.QtGame`
        :raises: None
        """
        return self.app.session.top_games(limit=5)

    def create_submenus(self, topgames):
        """Create submenus

        :param topgames: the top games
        :type topgames: :class:`list` of :class:`pytwitcher.models.QtGame`
        :returns: None
        :rtype: None
        :raises: None
        """
        for game in topgames:
            m = GameMenu(self.app, game, self)
            self.addMenu(m)


class GameMenu(IconLazyMenu):
    """A menu for a game wich can load the top streams
    """

    def __init__(self, app, game, parent=None):
        """Initialize a new game menu

        :param app: the pytwitcher app
        :type app: :class:`pytwitcher.app.PyTwicherApp`
        :param game: the game of the menu
        :type game: :class:`pytwicher.models.QtGame`
        :param parent: the parent widget
        :type parent: :class:`QtGui.QWidget`
        :raises: None
        """
        super(GameMenu, self).__init__(app, game.name, parent)
        self.game = game
        self.start_loading()
        self.start_icon_loading()

    def load_data(self, ):
        """Return the top streams of the game

        :returns: the top streams
        :rtype: :class:`list` of :class:`pytwitcher.models.QtStream`
        :raises: None
        """
        return self.game.top_streams(limit=10)

    def create_submenus(self, topstreams):
        """Create submenus

        :param topstreams: the top streams for the game
        :type topstreams: :class:`list` of :class:`pytwitcher.models.QtStream`
        :returns: None
        :rtype: None
        :raises: None
        """
        for stream in topstreams:
            m = StreamMenu(self.app, stream, self)
            self.addMenu(m)

    def load_icon(self, ):
        """This function gets called in another thread and should return data for
        :meth:`LazyMenu.create_icon`.

        Override this function.

        :returns: The bytearray for the pixmap
        :rtype: :class:`QtCore.QByteArray`
        :raises: None
        """
        url = self.game.logo["small"]
        return self.game.cache.bytearraycache[url]

    def create_icon(self, data):
        """Create and return icon from the data received by the lazy loading

        Override this function!

        :param data: the data returned from :meth:`LazyMenu.load_icon`
        :returns: the created icon
        :rtype: :class:`QtGui.QIcon`
        :raises: None
        """
        return QtGui.QIcon(self.game.get_box("small"))


class StreamMenu(IconLazyMenu):
    """A menu for a single stream which can load
    the quality options for a stream and add them as submenu.
    """

    def __init__(self, app, stream, parent=None):
        """Initialize a new stream menu

        :param app: the pytwitcher app
        :type app: :class:`pytwitcher.app.PyTwicherApp`
        :param stream: the stream to represent
        :type stream: :class:`pytwicher.models.QtStream`
        :raises: None
        """
        super(StreamMenu, self).__init__(app, stream.channel.name, parent)
        self.app = app
        self.stream = stream
        self.setToolTip(stream.channel.status)
        self.start_loading()
        self.start_icon_loading()

    def load_data(self, ):
        """Return the quality options for the stream

        :returns: the quality options
        :rtype: :class:`list` of :class:`str`
        :raises: None
        """
        return self.stream.quality_options

    def create_submenus(self, options):
        """Create submenus for each option

        :param options: the quality options
        :type options: :class:`list` :class:`str`
        :returns: None
        :rtype: None
        :raises: None
        """
        for option in options:
            a = QualityOptionAction(self.app, self.stream, option, self)
            self.addAction(a)

    def load_icon(self, ):
        """This function gets called in another thread and should return data for
        :meth:`LazyMenu.create_icon`.

        Override this function.

        :returns: The bytearray for the pixmap | None
        :rtype: :class:`QtCore.QByteArray`
        :raises: None
        """
        url = self.stream.channel._smalllogo
        if url:
           return self.stream.cache.bytearraycache[url]

    def create_icon(self, data):
        """Create and return icon from the data received by the lazy loading

        Override this function!

        :param data: the data returned from :meth:`LazyMenu.load_icon`
        :returns: the created icon
        :rtype: :class:`QtGui.QIcon`
        :raises: None
        """
        if data:
            return QtGui.QIcon(self.stream.channel.smalllogo)


class QualityOptionAction(QtGui.QAction):
    """Shows a quality option for a stream.
    And triggers to show the stream when clicked on.
    """

    def __init__(self, app, stream, option, parent=None):
        """Initialize a new QualityOptionAction

        :raises: None
        """
        super(QualityOptionAction, self).__init__(option, parent)
        self.option = option
        self.app = app
        self.stream = stream
        self.triggered.connect(self.play)

    def play(self, ):
        """Play the stream

        :returns: None
        :rtype: None
        :raises: None
        """
        self.stream.play(self.option)


class LoginAction(QtGui.QAction):
    """Login Action"""

    def __init__(self, app, parent=None):
        super(LoginAction, self).__init__("Login", parent)
        self.app = app
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
            name = self.app.session.current_user.name
            self.setText("%s" % name)
            self.followmenu = FollowMenu(self.app, self.parent())
            self.parent().insertMenu(
                self.parent().seperator1, self.followmenu)
        else:
            self.setText("Login")
            self.triggered.connect(self.login)


class FollowMenu(LazyMenu):
    """
    """

    def __init__(self, app, parent=None):
        """

        :param app:
        :type app:
        :param parent:
        :type parent:
        :raises: None
        """
        super(FollowMenu, self).__init__(app, "Following", parent)
        self.start_loading()

    def load_data(self, ):
        """Return data for submenus

        :returns: The followed streams
        :rtype: :class:`list` of :class:`pytwitcher.models.QtStream`
        :raises: None
        """
        return self.app.session.followed_streams()

    def create_submenus(self, followedstreams):
        """Create submenus

        :param followedstreams: the followed streams
        :type followedstreams: :class:`list` of
                               :class:`pytwitcher.models.QtStream`
        :returns: None
        :rtype: None
        :raises: None
        """
        for stream in followedstreams:
            m = StreamMenu(self.app, stream, self)
            self.addMenu(m)
