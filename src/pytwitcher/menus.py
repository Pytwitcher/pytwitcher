"""Module for the main menu that will be displayed at the top
off the application and as a context menu of the tray icon."""

import logging
import sys

from PySide import QtGui, QtCore

if sys.version_info[0] == 2:
    import futures
else:
    import concurrent.futures as futures

log = logging.getLogger(__name__)


class LazyMenu(QtGui.QMenu):
    """Menu which emits the menu action the first time
    it is clicked on.

    Call :meth:`LazyMenu.start_loading` manually.
    """

    loadingfinished = QtCore.Signal(futures.Future)

    def __init__(self, app, *args, **kwargs):
        """Initialize a new ActionMenu"""
        super(LazyMenu, self).__init__(*args, **kwargs)
        self.app = app
        self._activated = False
        self.add_done_callback(self._receive_data)

    def add_done_callback(self, func):
        self.loadingfinished.connect(func, type=QtCore.Qt.QueuedConnection)

    def start_loading(self,):
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

        :param future: the future from :meth:`LazyMenu.submit`
        :type future: :class:`concurrent.futures.Future`
        :returns: None
        :rtype: None
        :raises: None
        """
        self.clear()
        try:
            result = future.result()
        except:
            log.exception('Error receiving data for menu %s' % self)
            a = self.addAction('Error! Click to try again.')
            a.triggered.connect(self.submit)
        else:
            self.create_submenus(result)

    def create_submenus(self, data):
        """Create submenus for the data received by the lazy loading

        Override this function!

        :param data: the data returned from :meth:`LazyMenu.load_data`
        :returns: None
        :rtype: None
        :raises: None
        """
        pass


class MainMenu(QtGui.QMenu):
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

        self.add_submenus()

    def add_submenus(self, ):
        """Add submenus to the main menu

        :returns: None
        :rtype: None
        :raises: None
        """
        self.streamsmenu = StreamsMenu(self.app)
        self.helpaction = QtGui.QAction("Help", self)
        self.helpaction.triggered.connect(self.app.show_help)
        self.quitaction = QtGui.QAction("Quit", self)
        self.quitaction.triggered.connect(self.app.quit_app)

        self.addMenu(self.streamsmenu)
        self.addSeparator()
        self.addAction(self.helpaction)
        self.addSeparator()
        self.addAction(self.quitaction)


class StreamsMenu(LazyMenu):
    """Menu with top games which updates itself periodically
    """

    def __init__(self, app, label="Streams"):
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
        return self.app.session.top_games()

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


class GameMenu(LazyMenu):
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

    def load_data(self, ):
        """Return the top streams of the game

        :returns: the top streams
        :rtype: :class:`list` of :class:`pytwitcher.models.QtStream`
        :raises: None
        """
        return self.game.top_streams()

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


class StreamMenu(LazyMenu):
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
        label = "%s: %s" % (stream.channel.name, stream.channel.status)
        super(StreamMenu, self).__init__(app, label, parent)
        self.app = app
        self.stream = stream
        self.start_loading()

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
