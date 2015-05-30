"""Module for the main menu that will be displayed at the top
off the application and as a context menu of the tray icon."""

from PySide import QtGui


class ActionMenu(QtGui.QMenu):
    """Menu which emits the menu action the first time
    it is clicked on.
    """
    def __init__(self, *args, **kwargs):
        """Initialize a new ActionMenu"""
        super(ActionMenu, self).__init__(*args, **kwargs)
        self._activated = False
        self.slots = []

    def connect_action(self, slot):
        """Connect the given slot to the action
        which gets triggered the first time you click on the menu.

        :param slot: the callback to connect
        :returns: None
        :rtype: None
        :raises: None
        """
        print "connect", slot
        self.slots.append(slot)
        self.menuAction().triggered.connect(slot)

    def mousePressEvent(self, e):
        """Emit :meth:`QtGui.QMenu.menuAction` triggered signal.

        :param e: The event happening
        :type e: :class:`QtGui.QMouseEvent`
        :returns: None
        """
        r = super(ActionMenu, self).mousePressEvent(e)
        if not self._activated and not self.actionAt(e.pos()):
            self._activated = True
            self.menuAction().triggered.emit()
        return r


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


class StreamsMenu(QtGui.QMenu):
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
        super(StreamsMenu, self).__init__(label)
        self.app = app
        """The pytwicherapp that created this menu"""
        self.app.data.add_refresher('top_games', self.app.session.top_games)
        self.app.data.refresh_ended.connect(self.update_menu)
        self.addAction("Loading...")

    def update_menu(self, refresher):
        """Update the menu, if the refresher is "top_games"

        :param refresher: has to be "top_games" in order to refresh.
        :type refresher: :class:`str`
        :returns: None
        :rtype: None
        :raises: None
        """
        if refresher != "top_games":
            return
        self.clear()
        for game in self.app.data.top_games:
            m = GameMenu(self.app, game, self)
            self.addMenu(m)
        print "Added games"


class GameMenu(ActionMenu):
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
        super(GameMenu, self).__init__(game.name, parent)
        self.app = app
        self.game = game
        self.connect_action(self.load_topstreams)

    def load_topstreams(self, ):
        """Load the topstreams and create submenues

        :returns: None
        :rtype: None
        :raises: None
        """
        self.addAction("Loading...")
        self.app.qapp.processEvents()
        topstreams = self.game.top_streams()
        self.clear()
        for stream in topstreams:
            m = StreamMenu(self.app, stream, self)
            self.addMenu(m)


class StreamMenu(ActionMenu):
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
        super(StreamMenu, self).__init__(label, parent)
        self.app = app
        self.stream = stream
        self.connect_action(self.load_quality_options)

    def load_quality_options(self, ):
        """Load the quality options an create submenues

        :returns: None
        :rtype: None
        :raises: None
        """
        self.addAction("Loading...")
        self.app.qapp.processEvents()
        options = self.stream.quality_options
        self.clear()
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
