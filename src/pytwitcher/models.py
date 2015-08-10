"""This module contains wrappers around Twitch API objects.
They are all subclasses of the classes in :mod:`pytwitcherapi.models`.

They automatically load pictures using the :class:`pytwitcher.cache.PixmapLoader`.
Their intent is the usage in GUI Applications. The classes of :mod:`pytwitcherapi.models` are for none GUI Applications.
"""
import functools
import subprocess
import sys
import types

from PySide import QtCore, QtGui
from easymodel import treemodel

if sys.version_info[0] == 2:
    import futures
else:
    import concurrent.futures as futures

from pytwitcherapi import models


class QtGame(models.Game):
    """A class for twitch.tv Games.

    Automatically loads pictures and stores the topstreams.
    """

    @classmethod
    def from_game(cls, session, cache, game):
        """Create a QtGame from a :class:`pytwitcherapi.models.Game`

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param name: The name of the game
        :param game: the game to wrap
        :type game: :class:`pytwitcherapi.models.Game`
        :returns: a QtGame
        :rtype: :class:`pytwitcher.models.QtGame`
        :raises: None
        """
        return cls(session, cache, game.name, game.box, game.logo,
                   game.twitchid, game.viewers, game.channels)

    def __init__(self, session, cache, name, box, logo, twitchid, viewers=None, channels=None):
        """Initialize a new game

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param name: The name of the game
        :type name: :class:`str`
        :param box: Links for the box logos
        :type box: :class:`dict`
        :param logo: Links for the game logo
        :type logo: :class:`dict`
        :param twitchid: The id used by twitch
        :type twitchid: :class:`int`
        :param viewers: The current amount of viewers
        :type viewers: :class:`int`
        :param channels: The current amount of channels
        :type channels: :class:`int`
        :raises: None
        """
        super(QtGame, self).__init__(name, box, logo, twitchid, viewers, channels)
        self.session = session
        """The session that is used for Twitch API requests"""
        self.cache = cache
        """The picture cache to use"""
        self._top_streams = None

    def get_box(self, size):
        """Get a pixmap of the box logo in the requested size

        :param size: The size of the pixmap. Available values are
                     ``"large"``, ``"medium"``, ``"small"``.
        :type size: str
        :returns: the box logo
        :rtype: :class:`QtGui.QPixmap`
        :raises: :class:`KeyError` if size is wrong.
        """
        url = self.box[size]
        return self.cache[url]

    def get_logo(self, size):
        """Get a pixmap of the game logo in the requested size

        :param size: The size of the pixmap. Available values are
                     ``"large"``, ``"medium"``, ``"small"``.
        :type size: str
        :returns: the game logo
        :rtype: :class:`QtGui.QPixmap`
        :raises: :class:`KeyError` if size is wrong.
        """
        url = self.logo[size]
        return self.cache[url]

    def top_streams(self, limit=25, force_refresh=False):
        """Get the top streams of this game

        Top streams are cached and loaded the first time you call this function.
        You can force a refresh of those streams.
        If the limit is smaller than the amount of stored streams, only the amount of limit is returned.
        If the limit is **bigger** than the amount ofstored streams,
        it will not trigger a refresh to load more streams!! You have to specify explicitly to refresh.

        :param limit: the maximum number of streams to return
        :type limit: :class:`int`
        :param force_refresh: If True, refresh all values.
        :type force_refresh: :class:`bool`
        :returns: a list of top streams
        :rtype: :class:`list` of :class:`QtStream`
        :raises: None
        """
        if self._top_streams is None or force_refresh:
            self._top_streams = self.session.get_streams(game=self, limit=limit)
        return self._top_streams[:limit]


class QtChannel(models.Channel):
    """A class for twitch.tv Channels.

    Automatically loads pictures.
    """

    @classmethod
    def from_channel(cls, session, cache, channel):
        """Create a QtChannel from a :class:`pytwitcherapi.models.Channel`

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param name: The name of the channel
        :param channel: the channel to wrap
        :type channel: :class:`pytwitcherapi.models.Channel`
        :returns: a QtChannel
        :rtype: :class:`pytwitcher.models.QtChannel`
        :raises: None
        """
        return cls(session, cache, channel.name, channel.status,
                   channel.displayname, channel.game, channel.twitchid,
                   channel.views, channel.followers, channel.url,
                   channel.language, channel.broadcaster_language,
                   channel.mature, channel.logo, channel.banner,
                   channel.video_banner, channel.delay)

    def __init__(self, session, cache, name, status, displayname, game,
                 twitchid, views, followers, url, language,
                 broadcaster_language, mature, logo, banner, video_banner,
                 delay):
        """Initialize a new game

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param name: The name of the channel
        :type name: :class:`str`
        :param status: The status
        :type status: :class:`str`
        :param displayname: The name displayed by the interface
        :type displayname: :class:`str`
        :param game: the game of the channel
        :type game: :class:`str`
        :param twitchid: the internal twitch id
        :type twitchid: :class:`int`
        :param views: the overall views
        :type views: :class:`int`
        :param followers: the follower count
        :type followers: :class:`int`
        :param url: the url to the channel
        :type url: :class:`str`
        :param language: the language of the channel
        :type language: :class:`str`
        :param broadcaster_language: the language of the broadcaster
        :type broadcaster_language: :class:`str`
        :param mature: If true, the channel is only for mature audiences
        :type mature: :class:`bool`
        :param logo: the link to the logos
        :type logo: :class:`str`
        :param banner: the link to the banner
        :type banner: :class:`str`
        :param video_banner: the link to the video banner
        :type video_banner: :class:`str`
        :param delay: stream delay
        :type delay: :class:`int`
        :raises: None
        """
        super(QtChannel, self).__init__(name, status, displayname, game,
                                        twitchid, views, followers, url,
                                        language, broadcaster_language, mature,
                                        logo, banner, video_banner, delay)
        self._logo = logo
        self._smalllogo = logo.replace('-300x300.', '-50x50.') if logo\
                          else None
        if self._logo == self._smalllogo:
            print(self._smalllogo)
        self._banner = banner
        self._video_banner = video_banner
        self.session = session
        """The session that is used for Twitch API requests"""
        self.cache = cache
        """The picture cache to use"""

    @property
    def logo(self, ):
        """Return the logo

        :returns: the logo
        :rtype: :class:`QtGui.QPixmap` | None
        :raises: None
        """
        if self._logo:
            return self.cache[self._logo]

    @logo.setter
    def logo(self, url):
        """Set the logo

        :param url: the url to the logo
        :type url: :class:`str`
        :returns: None
        :raises: None
        """
        self._logo = url

    @property
    def smalllogo(self, ):
        """Return the logo

        :returns: the logo
        :rtype: :class:`QtGui.QPixmap` | None
        :raises: None
        """
        if self._smalllogo:
            return self.cache[self._smalllogo]

    @smalllogo.setter
    def smalllogo(self, url):
        """Set the logo

        :param url: the url to the logo
        :type url: :class:`str`
        :returns: None
        :raises: None
        """
        self._smalllogo = url

    @property
    def banner(self, ):
        """Return the banner

        :returns: the banner
        :rtype: :class:`QtGui.QPixmap`
        :raises: None
        """
        return self.cache[self._banner]

    @banner.setter
    def banner(self, url):
        """Set the banner

        :param url: the url to the banner
        :type url: :class:`str`
        :returns: None
        :raises: None
        """
        self._banner = url

    @property
    def video_banner(self, ):
        """Return the video_banner

        :returns: the video_banner
        :rtype: :class:`QtGui.QPixmap`
        :raises: None
        """
        return self.cache[self._video_banner]

    @video_banner.setter
    def video_banner(self, url):
        """Set the video_banner

        :param url: the url to the video_banner
        :type url: :class:`str`
        :returns: None
        :raises: None
        """
        self._video_banner = url


class QtStream(models.Stream):
    """A class for twitch.tv Stream.

    Automatically loads pictures.
    """

    @classmethod
    def from_stream(cls, session, cache, stream):
        """Create a QtStream from a :class:`pytwitcherapi.models.Stream`

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param name: The name of the stream
        :param stream: the stream to wrap
        :type stream: :class:`pytwitcherapi.models.Stream`
        :returns: a QtStream
        :rtype: :class:`pytwitcher.models.QtStream`
        :raises: None
        """
        channel = QtChannel.from_channel(session, cache, stream.channel)
        return cls(session, cache, stream.game, channel, stream.twitchid,
                   stream.viewers, stream.preview)

    def __init__(self, session, cache, game, channel, twitchid, viewers, preview):
        """Initialize a new stream

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param game: name of the game
        :type game: :class:`str`
        :param channel: the channel that is streaming
        :type channel: :class:`Channel`
        :param twitchid: the internal twitch id
        :type twitchid: :class:`int`
        :param viewers: the viewer count
        :type viewers: :class:`int`
        :param preview: a dict with preview picture links of the stream
        :type preview: :class:`dict`
        :raises: None
        """
        super(QtStream, self).__init__(game, channel, twitchid, viewers, preview)
        self.session = session
        """The session that is used for Twitch API requests"""
        self.cache = cache
        """The picture cache to use"""
        self._quality_options = None

    def get_preview(self, size):
        """Get a pixmap of the box logo in the requested size

        :param size: The size of the pixmap. Available values are
                     ``"large"``, ``"medium"``, ``"small"``.
        :type size: str
        :returns: the box logo
        :rtype: :class:`QtGui.QPixmap`
        :raises: :class:`KeyError` if size is wrong.
        """
        url = self.preview[size]
        return self.cache[url]

    @property
    def quality_options(self):
        """Return a list with available quality options

        Possible values in the list:

          * source
          * high
          * medium
          * low
          * mobile
          * audio

        :returns: a list with options
        :rtype: :class:`list` of :class:`str`
        :raises: :class:`requests.HTTPError` if channel is offline and you call it the first time
        """
        if self._quality_options is None:
            qo = self.session.get_quality_options(self.channel)
            self._quality_options = qo
        return self._quality_options

    def play(self, quality=None):
        """Play the stream in the specified quality

        If no quality is specified, the highest available is used.

        :param quality: the quality. See :meth:`QtStream.quality_options`
        :type quality: :class:`str`
        :returns: the subprocess running livestreamer
        :rtype: :class:`subprocess.POpen`
        :raises: None
        """
        if quality is None:
            quality = self.quality_options[0]
        args = ['livestreamer', self.channel.url, quality]
        return subprocess.Popen(args)


class QtUser(models.User):
    """A class for twitch.tv User.

    Automatically loads pictures.
    """

    @classmethod
    def from_user(cls, session, cache, user):
        """Create a QtUser from a :class:`pytwitcherapi.models.User`

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param name: The name of the user
        :param user: the user to wrap
        :type user: :class:`pytwitcherapi.models.User`
        :returns: a QtUser
        :rtype: :class:`pytwitcher.models.QtUser`
        :raises: None
        """
        return cls(session, cache, user.usertype, user.name, user.logo,
                   user.twitchid, user.displayname, user.bio)

    def __init__(self, session, cache, usertype, name, logo, twitchid, displayname, bio):
        """Initialize a new user

        :param session: The session that is used for Twitch API requests
        :type session: :class:`pytwitcher.session.QtTwitchSession`
        :param cache: The picture cache to use
        :type cache: :class:`pytwitcher.cache.PixmapLoader`
        :param usertype: the user type on twitch, e.g. ``"user"``
        :type usertype: :class:`str`
        :param name: the username
        :type name: :class:`str`
        :param logo: the link to the logo
        :type logo: :class:`str`
        :param twitchid: the internal twitch id
        :type twitchid: :class:`int`
        :param displayname: the name diplayed by the interface
        :type displayname: :class:`str`
        :param bio: the user bio
        :type bio: :class:`str`
        :raises: None
        """
        super(QtUser, self).__init__(usertype, name, logo, twitchid, displayname, bio)
        self.session = session
        self.cache = cache
        self._logo = logo

    @property
    def logo(self, ):
        """Return the logo

        :returns: the logo
        :rtype: :class:`QtGui.QPixmap`
        :raises: None
        """
        return self.cache[self._logo]

    @logo.setter
    def logo(self, url):
        """Set the logo

        :param url: the url to the logo
        :type url: :class:`str`
        :returns: None
        :raises: None
        """
        self._logo = url


class Callbacker(object):
    """Object to execute the load_callback.

    This object has to live in the main thread,
    so the slot gets executed! If not, qt tries to execute
    the slot in the thread the callbacker was created in.
    Because the eventloop is running in the main thread,
    it will never get invoked.
    """

    @QtCore.Slot(object, str, QtCore.Signal, types.MethodType, str, futures.Future)
    def load_callback(self, obj, attr, signal, convertfunc, key, future):
        """Set the attr to the result of the future and emit the signal

        :param obj: the object to set the attribute on
        :param attr: the name of the attribute to set
        :type attr: :class:`str`
        :param signal: the signal to emit afterwards
        :type signal: :class:`QtCore.Signal`
        :param key: If key is not None, attr is considered a dict
        :type key:
        :param future: the future with the result
        :type future: :class:`futures.Future`
        :returns: None
        :rtype: None
        :raises: None
        """
        result = future.result()
        if convertfunc:
            result = convertfunc(result)
        if not key:
            setattr(obj, attr, result)
        else:
            d = getattr(obj, attr)
            d[key] = result
        signal.emit()


class DeferLoadMixin(QtCore.QObject):
    """Mixin for deferred loading
    """

    callbacker = Callbacker()
    """Object for the executing the callbacks. Should live in the main thread."""
    loadingFinished = QtCore.Signal(object, str, QtCore.Signal, types.MethodType, str, futures.Future)
    LOADING = 'LOADING'

    def __init__(self, *args, **kwargs):
        super(DeferLoadMixin, self).__init__(*args, **kwargs)
        self.loadingFinished.connect(self.callbacker.load_callback, type=QtCore.Qt.QueuedConnection)

    def dummyconvert(self, arg):
        """Needed so pyside can wrap the object when emitting the signal.
        Pyside trying to wrap None will result in a segfault.
        """
        return arg

    def deferload(self, loadfunc, attr, signal, convertfunc=None, key=''):
        """Defer calling loadfunc set attr with the result and emit signal

        :param loadfunc: the function to call for loading
        :type loadfunc: :class:`function`
        :param attr: the name of the attribute to set
        :type attr: :class:`str`
        :param signal: the signal to emit afterwards
        :type signal: :class:`QtCore.Signal`
        :param key: If key is not None, attr is considered a dict
        :returns: None
        :rtype: None
        :raises: None
        """
        if convertfunc is None:
            # needed so pyside can wrap the object when emitting the signal
            convertfunc = self.dummyconvert
        cb = functools.partial(self.loadingFinished.emit, self, attr, signal, convertfunc, key)
        future = self.session.pool.submit(loadfunc)
        future.add_done_callback(cb)

    def convert_to_pixmap(self, ba):
        """Convert the bytearray to a pixmap

        :param ba: the bytearray
        :type ba: :class:`QtCore.QByteArray`
        :returns: a pixmap
        :rtype: :class:`QtGui.QPixmap`
        :raises: None
        """
        p = QtGui.QPixmap()
        p.loadFromData(ba)
        return p

    def _handle_loading(self, attr, key):
        value = getattr(self, attr)
        if key is not None:
            value = value.get(key)
        if value is self.LOADING:
            return
        if value:
            return value
        if key is None:
            setattr(self, attr, self.LOADING)
        else:
            getattr(self, attr)[key] = self.LOADING

    def deferload_pixmap(self, attr, url, signal, key=None):
        """Use the deferload function to load the url and set it on the attribute

        :param attr: the attribute name that is used to store the pixmap
        :type attr: :class:`str`
        :param url: the url to load
        :type url: :class:`str`
        :param signal: the signal to emit after the loading is complete
        :type signal: :class:`QtCore.Signal`
        :param key: If the key is not None, consider the attribute as a dict
        :returns: None if loading hasn't finished or the pixmap
        :rtype: :class:`QtGui.QPixmap` | None
        :raises: None
        """
        value = self._handle_loading(attr, key)
        if value is not None:
            return value
        loadfunc = functools.partial(self.cache.bytearraycache.__getitem__, url)
        self.deferload(loadfunc, attr, signal, self.convert_to_pixmap, key)


class DeferQtGame(QtGame, DeferLoadMixin):
    """class for twitch.tv Games with deferred loading.

    Loads pictures and topstreams deferred.
    """

    boxLoaded = QtCore.Signal()
    logoLoaded = QtCore.Signal()
    topStreamsLoaded = QtCore.Signal()

    def __init__(self, session, cache, name, box, logo, twitchid, viewers=None, channels=None):
        super(DeferQtGame, self).__init__(session, cache, name, box, logo,
                                         twitchid, viewers, channels)
        DeferLoadMixin.__init__(self)
        self._box_pix = {}
        self._logo_pix = {}
    __init__.__doc__ = QtGame.__init__.__doc__

    def get_box(self, size):
        return self.deferload_pixmap('_box_pix', self.box[size], self.boxLoaded, size)
    get_box.__doc__ = QtGame.get_box.__doc__

    def get_logo(self, size):
        return self.deferload_pixmap('_logo_pix', self.logo[size], self.logoLoaded, size)
    get_logo.__doc__ = QtGame.get_logo.__doc__

    def top_streams(self, limit=25, force_refresh=False):
        if self._top_streams is self.LOADING:
            return
        if self._top_streams is None or force_refresh:
            self._top_streams = self.LOADING
            loadfunc = functools.partial(self.session.get_streams, game=self, limit=limit)
            self.deferload(loadfunc, '_top_streams', self.topStreamsLoaded)
            return []
        return self._top_streams[:limit]
    top_streams.__doc__ = QtGame.top_streams.__doc__


class DeferQtChannel(QtChannel, DeferLoadMixin):
    """Class for twitch.tv Channels with deferred loading.

    Loads pictures deferred.
    """

    logoLoaded = QtCore.Signal()
    smalllogoLoaded = QtCore.Signal()
    bannerLoaded = QtCore.Signal()
    videoBannerLoaded = QtCore.Signal()

    def __init__(self, session, cache, name, status, displayname, game,
                 twitchid, views, followers, url, language,
                 broadcaster_language, mature, logo, banner, video_banner,
                 delay):
        super(DeferQtChannel, self).__init__(session, cache, name, status, displayname,
                                            game, twitchid, views, followers, url,
                                            language, broadcaster_language, mature,
                                            logo, banner, video_banner, delay)
        DeferLoadMixin.__init__(self)
        self._logo_pix = None
        self._smalllogo_pix = None
        self._banner_pix = None
        self._video_banner_pix = None
    __init__.__doc__ = QtChannel.__init__.__doc__

    @QtChannel.logo.getter
    def logo(self):
        return self.deferload_pixmap('_logo_pix', self._logo, self.logoLoaded)

    @QtChannel.smalllogo.getter
    def smalllogo(self):
        return self.deferload_pixmap('_smalllogo_pix', self._smalllogo, self.smalllogoLoaded)

    @QtChannel.banner.getter
    def banner(self):
        return self.deferload_pixmap('_banner_pix', self._banner, self.bannerLoaded)

    @QtChannel.video_banner.getter
    def video_banner(self):
        return self.deferload_pixmap('_video_banner_pix', self._video_banner, self.videoBannerLoaded)


class DeferQtStream(QtStream, DeferLoadMixin):
    """Class for twitch.tv streams with deferred loading.

    Doads pictures and quality options deferred.
    """
    previewLoaded = QtCore.Signal()
    qualityOptionsLoaded = QtCore.Signal()

    @classmethod
    def from_stream(cls, session, cache, stream):
        channel = DeferQtChannel.from_channel(session, cache, stream.channel)
        return cls(session, cache, stream.game, channel, stream.twitchid,
                   stream.viewers, stream.preview)
    from_stream.__doc__ = QtStream.from_stream.__doc__

    def __init__(self, session, cache, game, channel, twitchid, viewers, preview):
        super(DeferQtStream, self).__init__(session, cache, game, channel, twitchid,
                                           viewers, preview)
        DeferLoadMixin.__init__(self)
        self._preview = {}
    __init__.__doc__ = QtStream.__init__.__doc__

    def get_preview(self, size):
        return self.deferload_pixmap('_preview', self.preview[size], self.previewLoaded, size)
    get_preview.__doc__ = QtStream.get_preview.__doc__

    @QtStream.quality_options.getter
    def quality_options(self):
        if self._quality_options is self.LOADING:
            return
        if self._quality_options:
            return self._quality_options
        self._quality_options = self.LOADING
        loadfunc = functools.partial(self.session.get_quality_options, self.channel)
        self.deferload(loadfunc, '_quality_options', self.qualityOptionsLoaded)
        return []


class DeferQtUser(QtUser, DeferLoadMixin):
    """Class for twitch.tv users with deferred loading.

    Loads the logo deferred.
    """

    logoLoaded = QtCore.Signal()

    def __init__(self, session, cache, usertype, name, logo, twitchid, displayname, bio):
        super(DeferQtUser, self).__init__(session, cache, usertype, name, logo, twitchid,
                                     displayname, bio)
        DeferLoadMixin.__init__(self)
        self._logo_pix
    __init__.__doc__ = QtUser.__init__.__doc__

    @QtUser.logo.getter
    def logo(self):
        if self._logo_pix is self.LOADING:
            return
        if self._logo_pix:
            return self._logo_pix
        self._logo_pix = self.LOADING
        loadfunc = functools.partial(self.cache.bytearraycache.__getitem__, self._logo)
        self.deferload(loadfunc, '_logo_pix', self.logoLoaded, self.convert_to_pixmap)
        return


class BaseItemData(treemodel.ItemData, QtCore.QObject):
    """Item data that stores one object
    and procedurally queries it.
    Subclass the class and override the columns class attribute.
    It should be a list of functions, which take the object and a role as
    argument and return the data.
    """
    columns = []
    dataChanged = QtCore.Signal(int)
    """Signal gets emitted when the data changed
    in the specified column"""

    def __init__(self, internalobj):
        """Initialize a new base item data

        :raises: None
        """
        super(BaseItemData, self).__init__()
        self.internalobj = internalobj
        """The object that is stored internally and holds the data"""

    def column_count(self):
        """Return the number of columns that can be queried for data

        :returns: the number of columns
        :rtype: :class:`int`
        :raises: None
        """
        return len(self.columns)

    def data(self, column, role):
        """Return the data for the specified column and role

        The column addresses one attribute of the data.

        :param column: the data column
        :type column: int
        :param role: the data role
        :type role: QtCore.Qt.ItemDataRole
        :returns: data depending on the role
        :rtype:
        :raises: None
        """
        return self.columns[column](self, self.internalobj, role)

    def internal_data(self, ):
        """Return the object that holds the data

        :returns: the internalobj attribute
        :raises: None
        """
        return self.internalobj

    def flags(self, column):
        """Return the item flags for the item

        Default is QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        :param column: the column to query
        :type column: int
        :returns: the item flags
        :rtype: QtCore.Qt.ItemFlags
        :raises: None
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class GameItemData(BaseItemData):
    """item data which represents :class:`DeferQtGame`
    """

    def __init__(self, game, size='small'):
        """Initialize a new item data for the game

        :param game: the game to represents
        :type game: :class:`DeferQtGame`
        :param size: the size for the preview
        :type size: :class:`str`
        :raises: None
        """
        super(GameItemData, self).__init__(game)

        self.size = size
        """The size for the logos. 'large', 'medium' or 'small'"""
        self.internalobj.boxLoaded.connect(functools.partial(self.dataChanged.emit, 0))
        self.internalobj.logoLoaded.connect(functools.partial(self.dataChanged.emit, 3))

    def maindata(self, game, role):
        """Return the data for the given role

        Returns the name for :data:`QtCore.Qt.DisplayRole`.
        Returns the box for :data:`QtCore.Qt.DecorationRole`.

        :param game: The game to query
        :type game: :class:`QtGame`
        :param role: the item data role
        :type role: :data:`QtCore.Qt.ItemDataRole`
        :returns: the data
        :raises: None
        """
        if role == QtCore.Qt.DisplayRole:
            return game.name
        if role == QtCore.Qt.DecorationRole:
            return game.get_box(self.size)

    def viewersdata(self, game, role):
        """Return the viewer count for DisplayRole

        :param game: The game to query
        :type game: :class:`QtGame`
        :param role: the item data role
        :type role: :data:`QtCore.Qt.ItemDataRole`
        :returns: the viewer count
        :rtype: :class:`str` | None
        :raises: None
        """
        if role == QtCore.Qt.DisplayRole:
            return str(game.viewers)

    def channelsdata(self, game, role):
        """Return the channel count for DisplayRole

        :param game: The game to query
        :type game: :class:`QtGame`
        :param role: the item data role
        :type role: :data:`QtCore.Qt.ItemDataRole`
        :returns: the channel count
        :rtype: :class:`str` | None
        :raises: None
        """
        if role == QtCore.Qt.DisplayRole:
            return str(game.channels)

    def logodata(self, game, role):
        """Return the logo for DecorationRole

        :param game: The game to query
        :type game: :class:`QtGame`
        :param role: the item data role
        :type role: :data:`QtCore.Qt.ItemDataRole`
        :returns: the logo
        :rtype: :class:`QtGui.QPixmap` | None
        :raises: None
        """
        if role == QtCore.Qt.DecorationRole:
            return game.get_logo(self.size)

    columns = [maindata, viewersdata, channelsdata, logodata]


class StreamItemData(BaseItemData):
    """item data which represents :class:`DeferQtStream`
    """

    def __init__(self, stream, size='small'):
        """Initialize a new item data for the stream

        :param stream: the stream to represent
        :type stream: :class:`DeferQtStream`
        :param size: the size for the preview
        :type size: :class:`str`
        :raises: None
        """
        super(StreamItemData, self).__init__(stream)
        self.size = size
        """The size for the logos. 'large', 'medium' or 'small'"""
        self.internalobj.previewLoaded.connect(functools.partial(self.dataChanged.emit, 0))

    def maindata(self, stream, role):
        """Return the data for the given role

        Returns the name for :data:`QtCore.Qt.DisplayRole`.
        Returns the logo for :data:`QtCore.Qt.DecorationRole`.

        :param game: The game to query
        :type game: :class:`QtGame`
        :param role: the item data role
        :type role: :data:`QtCore.Qt.ItemDataRole`
        :returns: the data
        :raises: None
        """
        if role == QtCore.Qt.DisplayRole:
            return stream.channel.name
        if role == QtCore.Qt.ToolTipRole:
            return stream.channel.status
        if role == QtCore.Qt.DecorationRole:
            return stream.channel.smalllogo

    def viewersdata(self, stream, role):
        """Return the viewer count for DisplayRole

        :param game: The game to query
        :type game: :class:`QtGame`
        :param role: the item data role
        :type role: :data:`QtCore.Qt.ItemDataRole`
        :returns: the viewer count
        :rtype: :class:`str` | None
        :raises: None
        """
        if role == QtCore.Qt.DisplayRole:
            return str(stream.viewers)

    def previewdata(self, stream, role):
        if role == QtCore.Qt.DecorationRole:
            return stream.get_preview(self.size)

    columns = [maindata, viewersdata, previewdata]


class TreeItem(treemodel.TreeItem):
    """A treeitem which emits dateChanged if the itemdata emits it
    """

    def __init__(self, data, parent=None):
        super(TreeItem, self).__init__(data, parent)
        if isinstance(data, BaseItemData):
            data.dataChanged.connect(self.data_changed_cb)
    __init__.__doc__ = treemodel.TreeItem.__init__.__doc__

    def data_changed_cb(self, column):
        """Emit dataChanged for the index that represents the column

        :param column: the column that changed
        :type column: :class:`int`
        :returns: None
        :rtype: None
        :raises: None
        """
        if not self._model:
            return
        index = self.to_index(column)
        self._model.dataChanged.emit(index, index)


class GameItem(TreeItem):
    """TreeItem that automatically loads streams
    """

    def __init__(self, data, parent=None, maxstreams=25):
        """Initialize a new game item

        :param data: the GameItemData
        :type data: :class:`GameItemData`
        :param parent: the parent item
        :type parent: :class:`treemodel.TreeItem` | None
        :param maxstreams: limit for topstreams
        :type maxstreams: :class:`int`
        :raises: None
        """
        super(GameItem, self).__init__(data, parent)
        self.itemdata().internalobj.topStreamsLoaded.connect(self.create_topstreams)
        # start loading of top_streams
        self.itemdata().internalobj.top_streams(limit=maxstreams)
        self.maxstreams = maxstreams

    def create_topstreams(self, ):
        """Create topstreams items from the games topstreams

        :returns: None
        :rtype: None
        :raises: None
        """
        topstreams = self.itemdata().internalobj.top_streams(limit=self.maxstreams)
        for s in topstreams:
            data = StreamItemData(s, self.itemdata().size)
            StreamItem(data, self)


class StreamItem(TreeItem):
    """Treeitem that automatically loads the quality options
    """

    def __init__(self, data, parent=None):
        """Initialize a new stream item

        :param data: the StreamItemData
        :type data: :class:`StreamItemData`
        :param parent: the parent item
        :type parent: :class:`treemodel.TreeItem` | None
        :raises: None
        """
        super(StreamItem, self).__init__(data, parent)
        self.itemdata().internalobj.qualityOptionsLoaded.connect(self.create_qualityoptions)
        self.itemdata().internalobj.quality_options

    def create_qualityoptions(self, ):
        """Create Items for the quality options

        :returns: None
        :rtype: None
        :raises: None
        """
        qo = self.itemdata().internalobj.quality_options
        for o in qo:
            data = treemodel.ListItemData([o])
            treemodel.TreeItem(data, self)
