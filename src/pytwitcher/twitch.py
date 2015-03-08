"""API for communicating with twitch"""
from requests.sessions import Session


TWITCH_KRAKENURL = "https://api.twitch.tv/kraken/"
"""The baseurl for the twitch api"""

TWITCH_HEADER_ACCEPT = "application/vnd.twitchtv.v3+json"
"""The header for the ``Accept`` key to tell twitch which api version it should use"""

TWITCH_USHERURL = "http://usher.twitch.tv/api/"
"""The baseurl for the twitch usher api"""

TWITCH_APIURL = "http://api.twitch.tv/api/"
"""The baseurl for the old twitch api"""


class BaseSession(Session):
    """Session that stores a baseurl that will be prepended for every request
    """

    def __init__(self, baseurl=None):
        """Initialize a new BaseSession with the given baseurl

        :param baseurl: a url that will always be prepended for every request
        :type baseurl: :class:`str` | None
        :raises: None
        """
        super(BaseSession, self).__init__()
        self.baseurl = baseurl
        """The baseurl that gets prepended to every request url"""

    def request(self, method, url, **kwargs):
        """Constructs a :class:`requests.model.Request`, prepares it and sends it.
        Raises HTTPErrors by default.

        :param method: method for the new :class:`Request` object.
        :type method: :class:`str`
        :param url: URL for the new :class:`Request` object.
        :type url: :class:`str`
        :param kwargs: keyword arguments of :meth:`requests.session.Session.request`
        :returns: a resonse object
        :rtype: :class:`requests.model.Response`
        :raises: :class:`requests.exceptions.HTTPError`
        """
        fullurl = self.baseurl + url if self.baseurl else url
        r = super(BaseSession, self).request(method, fullurl, **kwargs)
        r.raise_for_status()
        return r


class KrakenSession(BaseSession):
    """Session for the twitch kraken api
    """

    def __init__(self, ):
        """Initialize a new kraken session

        :raises: None
        """
        super(KrakenSession, self).__init__(baseurl=TWITCH_KRAKENURL)
        self.headers.update({"Accept": TWITCH_HEADER_ACCEPT})


class UsherSession(BaseSession):
    """Session for the twitch usher api
    """

    def __init__(self, ):
        """Initialize a new usher session

        :raises: None
        """
        super(UsherSession, self).__init__(baseurl=TWITCH_USHERURL)


class APISession(BaseSession):
    """Session for the old twitch api
    """

    def __init__(self, ):
        """Initialize a new api session

        :raises: None
        """
        super(APISession, self).__init__(baseurl=TWITCH_APIURL)

    def get_channel_access_token(self, channel):
        """Return the token and sig for the given channel

        :param channel: the channel to get the access token for
        :type channel: :class:`str`
        :returns: The token and sig for the given channel
        :rtype: (:class:`unicode`, :class:`unicode`)
        :raises: None
        """
        r = self.get("channels/%s/access_token" % channel).json()
        return r["token"], r["sig"]


class APIObject(object):
    """Base class for all twitch api objects

    Stores the json object internally, which can be accessed via ``__getitem__``
    """

    def __init__(self, json=None):
        """Initialize a new APIObject

        :param json:
        :type json:
        :raises: None
        """
        super(APIObject, self).__init__()
        self._json = json or {}

    def __getitem__(self, key):
        """Get the item for the given key in the internal json

        :param key: the key for accessing the item. Must be a hashable object.
        :returns: The item for the given key
        :raises: KeyError
        """
        return self._json[key]


class Game(APIObject):
    """Game on twitch.tv
    """

    def __init__(self, json):
        """Initialize a new game

        :param json: the json you get as a response from twitch
        :type json: :class:`dict`
        :raises: None
        """
        super(Game, self).__init__(json=json)
