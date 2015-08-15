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

        self.gameview.clicked.connect(self.setgame)
        self.channelview.clicked.connect(self.setchannel)
        self.qoview.clicked.connect(self.play)
        self.followview.clicked.connect(self.setchannel)

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
        views = (('Following', 'followview'),
                 ('Games', 'gameview'),
                 ('Channels', 'channelview'),
                 ('Quality', 'qoview'))
        for tab, attr in views:
            v = TableView()
            setattr(self, attr, v)
            v.setSelectionMode(v.NoSelection)
            v.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
            v.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
            self.tab_widget.addTab(v, tab)
        self.gameview.setModel(self.app.topgamesmodel)
        self.followview.setModel(self.app.followingmodel)
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


class TableView(QtGui.QTableView):
    """Table view that looses the model, if the root index gets removed.

    This prevents the view from getting the root index assigned at reload.
    Instead, the model is set to None.
    """
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
