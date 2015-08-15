from PySide import QtGui, QtCore
from easymodel import treemodel

from pytwitcher import utils, player


class PyTwitcherWin(QtGui.QMainWindow):
    """The main pytwitcher gui
    """

    def __init__(self, app):
        """Inizialize a new pytwitcher window

        :param app: the main app
        :type app: :class:`PyTwitcherApp`
        :raises: None
        """
        super(PyTwitcherWin, self).__init__(None)
        self.app = app
        self.mainmenu = app.mainmenu
        self.setup_ui()
        self.mainmenu.streamsmenu.action_triggered.connect(self.play)

    def setup_ui(self, ):
        """Create the user interface

        :returns: None
        :rtype: None
        :raises: None
        """
        logo = utils.get_logo()
        self.setWindowIcon(logo)
        self.create_toolbar()

        self.tab_widget = QtGui.QTabWidget()
        self.reload_pb = QtGui.QPushButton('reload')
        self.tab_widget.setCornerWidget(self.reload_pb)
        self.reload_pb.clicked.connect(self.reload_cb)
        self.tab_widget.addTab(self.create_following_view(), 'Following')
        self.tab_widget.addTab(self.create_games_view(), 'Games')
        self.tab_widget.addTab(self.create_channels_view(), 'Channels')
        self.tab_widget.addTab(self.create_quality_view(), 'Quality')

        self.tab_widget.setCurrentWidget(self.gameview)
        self.player = player.VideoPlayer(self)
        self.tab_widget.addTab(self.player, 'Player')
        self.setCentralWidget(self.tab_widget)
        self.resize(600, 400)

    def create_toolbar(self, ):
        """Create the toolbar with the main menu

        :returns: None
        :rtype: None
        :raises: None
        """
        self.toolbar = QtGui.QToolBar()
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        for a in self.mainmenu.actions():
            self.toolbar.addAction(a)
            if a.isSeparator():
                continue
            w = self.toolbar.widgetForAction(a)
            w.setPopupMode(w.InstantPopup)
            w.setStyleSheet('QToolButton::menu-indicator { image: none; }')

    def _wrap_with_more_button(self, widget):
        w = QtGui.QWidget()
        lay = QtGui.QVBoxLayout()
        w.setLayout(lay)
        lay.addWidget(widget)
        w.more_pb = QtGui.QPushButton("More")
        lay.addWidget(w.more_pb)
        return w

    def create_following_view(self, ):
        """Create the view for the followed streams

        :returns: a widgret containing the view
        :rtype: :class:`QtGui.QWidget`
        :raises: None
        """
        self.followview = TableView()
        self.followview.setModel(self.app.followingmodel)
        self.followview.clicked.connect(self.setchannel)
        w = self._wrap_with_more_button(self.followview)
        w.more_pb.clicked.connect(self.load_more_follows)
        return w

    def create_games_view(self, ):
        """Create the view for the games

        :returns: a widgret containing the view
        :rtype: :class:`QtGui.QWidget`
        :raises: None
        """
        self.gameview = TableView()
        self.gameview.setModel(self.app.topgamesmodel)
        self.gameview.clicked.connect(self.setgame)
        self.gametab = self._wrap_with_more_button(self.gameview)
        self.gametab.more_pb.clicked.connect(self.load_more_games)
        return self.gametab

    def create_channels_view(self, ):
        """Create the view for the channels

        :returns: a widgret containing the view
        :rtype: :class:`QtGui.QWidget`
        :raises: None
        """
        self.channelview = TableView()
        self.channelview.clicked.connect(self.setchannel)
        self.channeltab = self._wrap_with_more_button(self.channelview)
        self.channeltab.more_pb.clicked.connect(self.load_more_channels)
        return self.channeltab

    def create_quality_view(self, ):
        """Create the view for quality options

        :returns: the created view
        :rtype: :class:`QtGui.QListView`
        :raises: None
        """
        self.qoview = QtGui.QListView()
        self.qoview.clicked.connect(self.play)
        return self.qoview

    def reload_cb(self, ):
        """Reload the currently open tab

        :returns: None
        :rtype: None
        :raises: None
        """
        w = self.tab_widget.currentWidget()
        i = w.rootIndex()
        m = w.model()
        if m == self.app.topgamesmodel:
            self.app.reloadGamesModel.emit(i)
        elif m == self.app.followingmodel:
            self.app.reloadFollowModel.emit(i)

    def setgame(self, index):
        if self.channelview.model() is not index.model():
            self.channelview.setModel(index.model())
        self.channelview.setRootIndex(index)
        self.tab_widget.setCurrentWidget(self.channeltab)

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

    def load_more_follows(self, *args, **kwargs):
        """Load more channels

        :returns: None
        :rtype: None
        :raises: None
        """
        pass

    def load_more_games(self, *args, **kwargs):
        """Load more channels

        :returns: None
        :rtype: None
        :raises: None
        """
        pass

    def load_more_channels(self, *args, **kwargs):
        """Load more channels

        :returns: None
        :rtype: None
        :raises: None
        """
        index = self.channelview.rootIndex()
        if not index.isValid():
            return
        gameitem = index.data(treemodel.TREEITEM_ROLE)
        gameitem.load_more_streams()


class TableView(QtGui.QTableView):
    """Table view that looses the model, if the root index gets removed.

    This prevents the view from getting the root index assigned at reload.
    Instead, the model is set to None.
    """
    def __init__(self, parent=None):
        """Initizlize a new table view

        :param parent: the parent widget
        :type parent: :class:`QtGui.QWidget`
        :returns: None
        :rtype: None
        :raises: None
        """
        super(TableView, self).__init__(parent)
        self.setSelectionMode(self.NoSelection)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.verticalHeader().hide()

    def setRootIndex(self, index):
        self.lastroot = index
        super(TableView, self).setRootIndex(index)

    def rowsAboutToBeRemoved(self, parent, start, end):
        # root has changed, because root was also removed
        # the root was reset to an invalid index
        # This means we might see data from another hierarchy level now
        # better set model to None
        if not self.rootIndex().isValid() and self.rootIndex() != self.lastroot:
            self.setModel(None)
            return
        super(TableView, self).rowsAboutToBeRemoved(parent, start, end)
