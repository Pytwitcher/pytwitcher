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

    def __init__(self, ):
        """Initialize a new TwitchSession

        :raises: None
        """
        super(QtTwitchSession, self).__init__()
        self.cache = cache.PixmapLoader(self)
        """The cache to use for storing images (:class:`QtGui.QPixmap`)"""

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
        qtstreams = []
        streams = super(QtTwitchSession, self).get_streams(game=game, channels=channels,
                                                           limit=limit, offset=offset)
        for s in streams:
            qts = models.QtStream.from_stream(self, self.cache, s)
            qtstreams.append(qts)
        return qtstreams
