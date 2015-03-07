"""API for communicating with twitch"""
from requests.sessions import Session


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
