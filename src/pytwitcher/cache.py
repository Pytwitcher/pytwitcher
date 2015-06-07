"""This module contains classes for caching data"""
import collections
import types

from PySide import QtGui, QtCore


class Defaultdict(collections.defaultdict):
    """A defaultdict wich passes key to the default factory."""
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class ByteArrayLoader(Defaultdict):
    """A dict like object that loads and stores bytearrays

    Keys are urls to pictures. Values are :class:`QtCore.QByteArray`.
    If the key is not in the dict, the picture will be downloaded, stored,
    and returned
    """

    def __init__(self, session):
        """Initialize a new, empty cache that uses the given session
        for downloads.

        :param session: The session used for downloads
        :type session: :class:`requests.Session`
        :raises: None
        """
        super(ByteArrayLoader, self).__init__(self.load_picture)
        self.session = session

    def load_picture(self, url):
        """Load the picture at the given url

        :param url: the url to the picture
        :type url: :class:`str`
        :returns: a bytearray of the picture data
        :rtype: :class:`QtCore.QByteArray`
        :raises: None
        """
        r = self.session.get(url)
        return QtCore.QByteArray(r.content)


class PixmapLoader(Defaultdict):
    """A dict like object that loads and stores pixmaps

    Keys are urls to pictures. Values are :class:`QtGui.QPixmap`.
    If the key is not in the dict, the picture will be downloaded,
    stored and returned.
    """

    def __init__(self, session):
        """Initialize a new, empty cache that uses the given session
        for downloads.

        :param session: The session used for downloads
        :type session: :class:`requests.Session`
        :raises: None
        """
        super(PixmapLoader, self).__init__(self.load_picture)
        self.bytearraycache = ByteArrayLoader(session)
        self.session = session

    def load_picture(self, url):
        """Load the picutre at the given url

        :param url:
        :type url:
        :returns: a pixmap with the picture
        :rtype: :class:`QtGui.QPixmap`
        :raises: :class:`requests.HTTPError`
        """
        c = self.bytearraycache[url]
        p = QtGui.QPixmap()
        p.loadFromData(c)
        return p
