"""API for communicating with twitch

This module wraps the :class:`pytwitcherapi.session.TwitchSession` to use
the models of :mod:`pytwitcher.models`.
"""
from pytwitcher import cache, models
from pytwitcherapi import session


class QtTwitchSession(session.TwitchSession):
    """Session for easy requests to the Twitch APIs.

    Uses the models of :mod:`pytwitcher.models`.
    """

    def __init__(self, pool=None):
        """Initialize a new TwitchSession

        :param pool: a executor for deferred loading
        :type pool: :class:`futures.Executor`
        :raises: None
        """
        super(QtTwitchSession, self).__init__()
        self.pool = pool
        """A executor for deferred loading"""
        self.cache = cache.PixmapLoader(self)
        """The cache to use for storing images (:class:`QtGui.QPixmap`)"""

    def search_games(self, query, live=True):
        """Search for games that are similar to the query

        :param query: the query string
        :type query: :class:`str`
        :param live: If true, only returns games that are live on at least one
                     channel
        :type live: :class:`bool`
        :returns: A list of games
        :rtype: :class:`list` of :class:`models.QtGame` instances
        :raises: None
        """
        games = super(QtTwitchSession, self).search_games(query=query, live=live)
        qtgames = [models.DeferQtGame.from_game(self, self.cache, g) for g in games]
        return qtgames

    def top_games(self, limit=10, offset=0):
        """Return the current top games

        :param limit: the maximum amount of top games to query
        :type limit: :class:`int`
        :param offset: the offset in the top games
        :type offset: :class:`int`
        :returns: a list of top games
        :rtype: :class:`list` of :class:`models.QtGame`
        :raises: None
        """
        games = super(QtTwitchSession, self).top_games(limit=limit, offset=offset)
        qtgames = [models.DeferQtGame.from_game(self, self.cache, g) for g in games]
        return qtgames

    def get_game(self, name):
        """Get the game instance for a game name

        :param name: the name of the game
        :type name: :class:`str`
        :returns: the game instance
        :rtype: :class:`models.QtGame` | None
        :raises: None
        """
        game = super(QtTwitchSession, self).get_game(name=name)
        if game is None:
            return None
        qtgame = models.DeferQtGame.from_game(self, self.cache, game)
        return qtgame

    def get_channel(self, name):
        """Return the channel for the given name

        :param name: the channel name
        :type name: :class:`str`
        :returns: :class:`models.QtChannel`
        :rtype: None
        :raises: None
        """
        channel = super(QtTwitchSession, self).get_channel(name=name)
        if channel is None:
            return None
        qtchannel = models.DeferQtChannel.from_channel(self, self.cache, channel)
        return qtchannel

    def search_channels(self, query, limit=25, offset=0):
        """Search for channels and return them

        :param query: the query string
        :type query: :class:`str`
        :param limit: maximum number of results
        :type limit: :class:`int`
        :param offset: offset for pagination
        :type offset: :class:`int`
        :returns: A list of channels
        :rtype: :class:`list` of :class:`models.QtChannel` instances
        :raises: None
        """
        channels = super(QtTwitchSession, self).search_channels(query=query, limit=limit, offset=offset)
        qtchannels = [models.DeferQtChannel.from_channel(self, self.cache, c) for c in channels]
        return qtchannels

    def get_stream(self, channel):
        """Return the stream of the given channel

        :param channel: the channel that is broadcasting.
                        Either name or models.Channel instance
        :type channel: :class:`str` | :class:`models.Channel`
        :returns: the stream or None, if the channel is offline
        :rtype: :class:`models.QtStream` | None
        :raises: None
        """
        stream = super(QtTwitchSession, self).get_stream(channel=channel)
        if stream is None:
            return None
        qtstream = models.DeferQtStream.from_stream(self, self.cache, stream)
        return qtstream

    def get_streams(self, game=None, channels=None, limit=25, offset=0):
        """Return a list of streams queried by a number of parameters
        sorted by number of viewers descending

        :param game: the game or name of the game
        :type game: :class:`str` | :class:`models.Game`
        :param channels: list of models.Channels or channel names (can be mixed)
        :type channels: :class:`list` of :class:`models.Channel` or :class:`str`
        :param limit: maximum number of results
        :type limit: :class:`int`
        :param offset: offset for pagination
        :type offset: :class:`int`
        :returns: A list of streams
        :rtype: :class:`list` of :class:`models.QtStream`
        :raises: None
        """
        streams = super(QtTwitchSession, self).get_streams(game=game, channels=channels,
                                                           limit=limit, offset=offset)
        qtstreams = [models.DeferQtStream.from_stream(self, self.cache, s) for s in streams]
        return qtstreams

    def search_streams(self, query, hls=False, limit=25, offset=0):
        """Search for streams and return them

        :param query: the query string
        :type query: :class:`str`
        :param hls: If true, only return streams that have hls stream
        :type hls: :class:`bool`
        :param limit: maximum number of results
        :type limit: :class:`int`
        :param offset: offset for pagination
        :type offset: :class:`int`
        :returns: A list of streams
        :rtype: :class:`list` of :class:`models.QtStream` instances
        :raises: None
        """
        streams = super(QtTwitchSession, self).search_streams(query=query, hls=hls,
                                                              limit=limit, offset=offset)
        qtstreams = [models.DeferQtStream.from_stream(self, self.cache, s) for s in streams]
        return qtstreams

    def followed_streams(self, limit=25, offset=0):
        """Return the streams the current user follows.

        Needs authorization ``user_read``.

        :param limit: maximum number of results
        :type limit: :class:`int`
        :param offset: offset for pagination
        :type offset::class:`int`
        :returns: A list of streams
        :rtype: :class:`list`of :class:`models.Stream` instances
        :raises: :class:`exceptions.NotAuthorizedError`
        """
        streams = super(QtTwitchSession, self).followed_streams(limit=limit,
                                                                offset=offset)
        qtstreams = [models.DeferQtStream.from_stream(self, self.cache, s) for s in streams]
        return qtstreams

    def get_user(self, name):
        """Get the user for the given name

        :param name: The username
        :type name: :class:`str`
        :returns: the user instance
        :rtype: :class:`models.User`
        :raises: None
        """
        user = super(QtTwitchSession, self).get_user(name=name)
        if user is None:
            return None
        qtuser = models.DeferQtUser.from_user(self, self.cache, user)
        return qtuser

    def fetch_login_user(self, ):
        """Set and return the currently logined user

        Sets :data:`QtTwitchSession.current_user`

        :returns: The user instance
        :rtype: :class:`models.QtUser`
        :raises: :class:`NotAuthorizedError`
        """
        user = super(QtTwitchSession, self).fetch_login_user()
        self.current_user = models.DeferQtUser.from_user(self, self.cache, user)
        return self.current_user
