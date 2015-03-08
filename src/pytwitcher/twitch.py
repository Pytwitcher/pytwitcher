"""API for communicating with twitch"""
from requests.sessions import Session


TWITCH_KRAKENURL = 'https://api.twitch.tv/kraken/'
"""The baseurl for the twitch api"""

TWITCH_HEADER_ACCEPT = 'application/vnd.twitchtv.v3+json'
"""The header for the ``Accept`` key to tell twitch which api version it should use"""

TWITCH_USHERURL = 'http://usher.twitch.tv/api/'
"""The baseurl for the twitch usher api"""

TWITCH_APIURL = 'http://api.twitch.tv/api/'
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

    @classmethod
    def get_instance(cls, ):
        """Get a global instance or create if it does not already exist

        :returns: A session instance
        :rtype: :class:`BaseSession`
        :raises: None
        """
        if '_instance' not in cls.__dict__ or not cls._instance:
            cls._instance = cls()
        return cls._instance

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
        self.headers.update({'Accept': TWITCH_HEADER_ACCEPT})


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
        r = self.get('channels/%s/access_token' % channel).json()
        return r['token'], r['sig']


class Game(object):
    """Game on twitch.tv
    """

    @classmethod
    def wrap_search(cls, response):
        """Wrap the response from a game search into instances
        and return them

        :param response: The response from searching a game
        :type response: :class:`requests.models.Response`
        :returns: the new game instances
        :rtype: :class:`Game`
        :raises: None
        """
        games = []
        json = response.json()
        gamejsons = json['games']
        for j in gamejsons:
            g = cls.wrap_json(j)
            games.append(g)
        return games

    @classmethod
    def wrap_topgames(cls, response):
        """Wrap the response from quering the top games into instances
        and return them

        :param response: The response for quering the top games
        :type response: :class:`requests.models.Response`
        :returns: the new game instances
        :rtype: :class:`Game`
        :raises: None
        """
        games = []
        json = response.json()
        topjsons = json['top']
        for t in topjsons:
            g = cls.wrap_json(json=t['game'],
                              viewers=t['viewers'],
                              channels=t['channels'])
            games.append(g)
        return games

    @classmethod
    def wrap_json(cls, json, viewers=None, channels=None):
        """Create a Game instance for the given json

        :param json: the dict with the information of the game
        :type json: :class:`dict`
        :param viewers: The viewer count
        :type viewers: :class:`int`
        :param channels: The viewer count
        :type channels: :class:`int`
        :returns: the new game instance
        :rtype: :class:`Game`
        :raises: None
        """
        g = Game(name=json['name'],
                 box=json['box'],
                 logo=json['logo'],
                 twitchid=json['_id'],
                 viewers=viewers,
                 channels=channels)
        return g

    def __init__(self, name, box, logo, twitchid, viewers=None, channels=None):
        """Initialize a new game

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
        self.name = name
        """The name of the game"""
        self.box = box
        """Links for the box logos"""
        self.logo = logo
        """Links for the logos"""
        self.twitchid = twitchid
        """Id used by twitch"""
        self.viewers = viewers
        """Current amount of viewers"""
        self.channels = channels
        """Current amount of channels"""

        if viewers is None or channels is None:
            self.fetch_viewers()

    def fetch_viewers(self, ):
        """Query the viewers and channels of this game and
        set them on the object

        :returns: None
        :rtype: None
        :raises: None
        """
        ks = KrakenSession.get_instance()
        r = ks.get('streams/summary', params={'game': self.name}).json()
        self.viewers = r['viewers']
        self.channels = r['channels']
