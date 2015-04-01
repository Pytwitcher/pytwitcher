"""This module contains classes for caching data"""
import types

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


class DataRefresher(QtCore.QObject):
    """Stores data and refreshes them in intervals

    Can also refresh manually.
    """

    refresh_all_started = QtCore.Signal()
    """This signal will get emitted, before refreshing starts."""
    refresh_all_ended = QtCore.Signal()
    """This signal will get emitted, after all data is refreshed."""
    refresh_started = QtCore.Signal(str)
    """This signal will get emmited, before refreshing of an attribute starts."""
    refresh_ended = QtCore.Signal(str)
    """This signal will get emmited, after an attribute is refreshed."""

    def __init__(self, interval, parent=None):
        """Initialize a new datarefresher

        :param interval: the refresh interval in miliseconds
        :type interval: :class:`int`
        :param parent: the parent qobject
        :type parent: :class:`QtCore.QObject`
        :raises: None
        """
        super(DataRefresher, self).__init__(parent)
        self._timer = QtCore.QTimer(self)
        self.set_interval(interval)
        self._timer.timeout.connect(self.refresh_all)
        self._refreshers = []

    def set_interval(self, interval):
        """Set the interval to the given one

        :param interval: the interval in miliseconds
        :type interval: :class:`int`
        :returns: None
        :rtype: None
        :raises: None
        """
        self._timer.setInterval(interval)

    def get_interval(self):
        """Return the interval of refreshing

        :returns: The interval in miliseconds
        :rtype: :class:`int`
        :raises: None
        """
        return self._timer.interval()

    def start(self, ):
        """Start the timer

        :returns: None
        :rtype: None
        :raises: None
        """
        self._timer.start()

    def stop(self, ):
        """Stop the timer

        :returns: None
        :rtype: None
        :raises: None
        """
        self._timer.stop()

    def add_refresher(self, name, refreshfunc):
        """Add a new attribute with the given name, that should be refreshed with
        the given function.

        :param name: the name of the attribute
        :type name: :class:`str`
        :param refreshfunc: the function to update the attribute. Should accept no arguments and
                            return a fresh value for the attribute on each call.
        :type refreshfunc: :class:`types.FunctionType`
        :returns: None
        :rtype: None
        :raises: :class:`ValueError` if the name is already an attribute or
                 cannot be used as attribute name.
        """
        d = dir(self)
        if name in d or 'refresh_%s' % name in d:
            raise ValueError("Cannot add attribute %s or 'refresh_%s', because there is already an attribute with this name." %
                             (name, name))
        setattr(self, name, None)

        def refresh(self):
            self.refresh_started.emit(name)
            new = refreshfunc()
            print new
            setattr(self, name, new)
            self.refresh_ended.emit(name)
        m = types.MethodType(refresh, self)
        setattr(self, 'refresh_%s' % name, m)
        self._refreshers.append(m)

    def refresh_all(self, ):
        """Refresh the whole data of the datarefresher

        :returns: None
        :rtype: None
        :raises: None
        """
        self.refresh_all_started.emit()
        for refresher in self._refreshers:
            refresher()
        self.refresh_all_ended.emit()
