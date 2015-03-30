"""This module contains wrappers around Twitch API objects.
They are all subclasses of the classes in :mod:`pytwitcherapi.models`.

They automatically load pictures using the :class:`pytwitcher.cache.PixmapLoader`.
Their intent is the usage in GUI Applications. The classes of :mod:`pytwitcherapi.models` are for none GUI Applications.
"""
from pytwitcherapi import models


class QtGame(models.Game):
    """A class for twitch.tv Games.

    Automatically loads pictures and stores the topstreams.
    """

    @classmethod
    def from_game(self, session, cache, game):
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
        return QtGame(session, cache, game.name, game.box, game.logo,
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

        :param limit: the maximum number of streams to return
        :type limit: :class:`int`
        :param force_refresh: If True, refresh all values.
        :type force_refresh: :class:`bool`
        :returns: a list of top streams
        :rtype: :class:`list` of :class:`QtStream`
        :raises: None
        """
        raise NotImplementedError


class QtChannel(models.Channel):
    """A class for twitch.tv Channels.

    Automatically loads pictures.
    """

    @classmethod
    def from_channel(self, session, cache, channel):
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
        return QtChannel(session, cache, channel.name, channel.status,
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
    def from_stream(self, session, cache, stream):
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
        channel  = QtChannel.from_channel(session, cache, stream.channel)
        return QtStream(session, cache, stream.game, channel, stream.twitchid,
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
