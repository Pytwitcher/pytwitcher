"""Utilities collection"""
import os
import pkg_resources

from PySide import QtGui


_logo = None


def get_logo():
    """Return the main logo for pytwicher.

    :returns: the main logo
    :rtype: :class:`QtGui.QIcon`
    :raises: None
    """
    global _logo
    if not _logo:
        logorelpath = os.path.join('data', 'icons', 'pytwicherlogo_64x64.png')
        logopath = pkg_resources.resource_filename('pytwitcher', logorelpath)
        _logo = QtGui.QIcon(QtGui.QPixmap(logopath))
    return _logo
