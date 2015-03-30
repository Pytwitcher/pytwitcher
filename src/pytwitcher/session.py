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
