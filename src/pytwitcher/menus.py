"""Module for the main menu that will be displayed at the top
off the application and as a context menu of the tray icon."""

import sys

from PySide import QtGui, QtCore

if sys.version_info[0] == 2:
    import futures
else:
    import concurrent.futures as futures


class LazyMenu(QtGui.QMenu):
    """Menu which emits the menu action the first time
    it is clicked on.
    """

    loadingfinished = QtCore.Signal(futures.Future)

    def __init__(self, app, *args, **kwargs):
        """Initialize a new ActionMenu"""
        super(LazyMenu, self).__init__(*args, **kwargs)
        self.app = app
        self._activated = False

    def add_done_callback(self, func):
        self.loadingfinished.connect(func, type=QtCore.Qt.QueuedConnection)

    def submit(self, func):
        future = self.app.pool.submit(func)
        future.add_done_callback(self.loadingfinished.emit)


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
        """Add submenues to the main menu

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
        self.add_done_callback(self.create_submenus)
        self.submit(self.app.session.top_games)
        self.addAction("Loading...")

    def create_submenus(self, future):
        """Create submenus

        :param future:
        :type future:
        :returns: None
        :rtype: None
        :raises: None
        """
        self.clear()
        try:
            topgames = future.result()
        except Exception as e:
            print e
            self.addAction("Error")
            return
        for game in topgames:
            m = GameMenu(self.app, game, self)
            self.addMenu(m)
        print "Added games"


class GameMenu(LazyMenu):
    """A menu for a game wich can load the top streams
    """

    loadingfinished = QtCore.Signal(futures.Future)

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
        self.add_done_callback(self.create_submenus)
        self.submit(self.game.top_streams)
        self.addAction("Loading...")

    def create_submenus(self, future):
        """Create submenues

        :returns: None
        :rtype: None
        :raises: None
        """
        self.clear()
        try:
            topstreams = future.result()
        except Exception as e:
            print e, self.game.name
            self.addAction("Error")
            return
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
        self.add_done_callback(self.load_quality_options)
        self.submit(lambda: self.stream.quality_options)
        self.addAction("Loading...")

    def load_quality_options(self, future):
        """Load the quality options an create submenues

        :returns: None
        :rtype: None
        :raises: None
        """
        self.clear()
        try:
            options = future.result()
        except Exception as e:
            print e, self.stream.game, self.stream.channel.name
            self.addAction("Error")
            return
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
