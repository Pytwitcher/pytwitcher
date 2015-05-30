"""Tray icon for the pytwitcherapp.

For the tray icon to work on Ubuntu, you might have to install the `sni-qt package <https://launchpad.net/sni-qt>`_.
"""
from pytwitcher import utils

from PySide import QtGui


class PytwitcherTray(QtGui.QSystemTrayIcon):
    """A tray icon for the pytwitcher app."""

    def __init__(self, menu):
        """Create a trayicon with logo and the given context menu

        :param menu: the menu for the tray icon
        :type menu: :class:`QtGui.QMenu`
        :returns: None
        :rtype: None
        :raises: None
        """
        super(PytwitcherTray, self).__init__()
        self.setContextMenu(menu)
        logo = utils.get_logo()
        self.setIcon(logo)
