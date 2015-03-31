"""This module contains classes for caching data"""
from PySide import QtGui, QtCore


class PixmapLoader(dict):
    """A dict like object that can loads and stores pixmaps

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
        super(PixmapLoader, self).__init__()
        self.session = session

    def __getitem__(self, key):
        """Retrieve a :class:`QtGui.QPixmap` for the given key.

        If the url has not been cached yet, the picture will be downloaded
        and stored.

        :param key: url to a picture
        :type key: :class:`str`
        :returns: the pixmap for the given url
        :rtype: :class:`QtGui.QPixmap`
        :raises: :class:`requests.HTTPError` if the picture cannot be downloaded.
        """
        if key in self:
            pixmap = super(PixmapLoader, self).get(key)
            return pixmap

        # download pixmap
        pixmap = self.load_picture(key)
        self[key] = pixmap
        return pixmap

    def load_picture(self, url):
        """Load the picutre at the given url

        :param url:
        :type url:
        :returns: a pixmap with the picture
        :rtype: :class:`QtGui.QPixmap`
        :raises: :class:`requests.HTTPError`
        """
        r = self.session.get(url)
        c = QtCore.QByteArray(r.content)
        p = QtGui.QPixmap()
        p.loadFromData(c)
        return p
