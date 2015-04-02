class PyTwitcherApp(object):
    """
    """

    def __init__(self, ):
        """
        
        :raises: None
        """
        super(PyTwitcherApp, self).__init__()
        self.session = session.QtTwitchSession()
        self.data = cache.DataRefresher(300000)
        self.data.add_refresher('top_games', self.session.top_games)
        self.data.refresh_ended.connect(self.update_menu)
        self.menu = QtGui.QMenu(self)

    def update_menu(self, name):
        """
        
        :param name:
        :type name:
        :returns: None
        :rtype: None
        :raises: None
        """
        if name != 'top_games':
            return
        self.menu.clear()
        for g in self.menu
