import sys

from PySide import QtGui, QtCore
from PySide.phonon import Phonon
import livestreamer


class VideoPlayer(QtGui.QWidget):
    """A videoplayer widget
    """

    def __init__(self, parent=None, flags=0):
        """Initialize a new videoplayer

        :param parent: the parent widget
        :type parent: :class:`QtGui.QWidget`
        :param flags: the window flags
        :type flags: :data:`QtCore.Qt.WindowFlags`
        :raises: None
        """
        super(VideoPlayer, self).__init__(parent, flags)
        self.streamer = livestreamer.Livestreamer()
        self.streamer.set_loglevel("info")
        self.streamer.set_logoutput(sys.stdout)
        self.main_hbox = QtGui.QHBoxLayout()
        self.main_hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_hbox)
        self.screen_widget = VideoScreen(self)
        self.screen_widget.installEventFilter(self)
        self.main_hbox.addWidget(self.screen_widget)

        self.player = Phonon.MediaObject()
        self.audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
        Phonon.createPath(self.player, self.screen_widget)
        Phonon.createPath(self.player, self.audio_out)
        self.streamdevice = None

    def play(self, stream, quality):
        """Play the given stream

        :param stream: the stream to play
        :type stream: :class:`pytwitcherapi.Stream`
        :param quality: the quality for the stream
        :type quality: :class:`str`
        :returns: None
        :rtype: None
        :raises: None
        """
        url = stream.channel.url
        try:
            streams = self.streamer.streams(url)
        except livestreamer.NoPluginError:
            self.screen_widget.set_status("Livestreamer is unable to handle the URL '%s'" % url)
            return
        except livestreamer.PluginError as err:
            self.screen_widget.set_status("Plugin error: %s" % err)
            return
        if not streams:
            self.screen_widget.set_status("No streams found on URL '%s'" % url)
            return
        elif quality not in streams:
            self.screen_widget.set_status("Unable to find '%s' stream on URL %s" % (quality, url))
        streamobj = streams[quality]
        if self.streamdevice:
            self.streamdevice.close()
        self.streamdevice = StreamDevice(streamobj, parent=self)
        media_src = Phonon.MediaSource(self.streamdevice)
        self.player.setCurrentSource(media_src)
        self.player.play()

    def eventFilter(self, obj, event):
        """Handle the events of obj

        :param obj: the object to handle the events for
        :type obj: :class:`QtCore.QObject`
        :param event: the event
        :type event: :class:`QtCore.QEvent`
        :returns: True, if the event shouldn't be forwarded further
        :rtype: :class:`bool`
        :raises: None
        """
        if obj is not self.screen_widget:
            return False
        if event.type() == QtCore.QEvent.Wheel and event.orientation() == QtCore.Qt.Vertical:
            d = event.delta() / 2400
            vol = self.audio_out.volume() + d
            if vol < 0:
                vol = 0
            if vol > 2.0:
                vol = 2.0
            self.audio_out.setVolume(vol)
            self.screen_widget.set_status("Volume: {0}%".format(int(vol * 100)))
        if event.type() == QtCore.QEvent.KeyRelease and event.key() == QtCore.Qt.Key_Space:
            if self.player.state() == Phonon.PausedState:
                self.player.play()
                self.screen_widget.set_status("Play")
            else:
                self.player.pause()
                self.screen_widget.set_status("Pause")
        return False


class VideoScreen(Phonon.VideoWidget):
    """A video widget that supports user interaction
    """

    def __init__(self, parent=None):
        """Initialize a new video screen

        :param parent: the parent widget
        :type parent: :class:`QtGui.QWidget`
        :raises: None
        """
        super(VideoScreen, self).__init__(parent)
        self.status_lb = QtGui.QLabel('', self)
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.hide_status)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def hide_status(self, ):
        """Hide the status label

        :returns: None
        :rtype: None
        :raises: None
        """
        self.status_lb.hide()

    def set_status(self, text, duration=2000):
        """Set the text of the status label for the given duration

        :param text: the text to set
        :type text: :class:`str`
        :param duration: the duration in milliseconds. 0 means infinite long.
        :type duration: :class:`int`
        :returns: None
        :rtype: None
        :raises: None
        """
        if duration == 0:
            self.timer.stop()
        else:
            self.timer.start(duration)
        self.status_lb.setText(text)
        self.status_lb.adjustSize()
        self.status_lb.show()

    def focusOutEvent(self, event):
        """Leave fullscreen

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: None
        :rtype: None
        :raises: None
        """
        if event.lostFocus():
            self.setFullScreen(False)
            event.accept()
            return
        return super(VideoScreen, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        """Enter or leave fullscreen mode

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: None
        :rtype: None
        :raises: None
        """
        if event.key() == QtCore.Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Enter or leave fullscreen mode

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: None
        :rtype: None
        :raises: None
        """
        fs = self.isFullScreen()
        self.setFullScreen(not fs)
        if not fs:
            self.set_status('Press ESC or double click to leave fullscreen mode!', 5000)
        event.accept()


class StreamDevice(QtCore.QIODevice):
    """IODevice for reading a stream"""
    def __init__(self, stream, parent=None):
        """Initialize a new stream device

        :param stream: the livestreamer stream
        :param parent: the parent object
        :type parent: :class:`QtCore.QObject`
        :raises: None
        """
        super(StreamDevice, self).__init__(parent)
        self.fd = stream.open()

    def readData(self, maxlen):
        data = self.fd.read(maxlen)
        if not data:
            self.fd.close()
        return data

    def writeData(self, data):
        return

    def close(self, *args, **kwargs):
        super(StreamDevice, self).close(*args, **kwargs)
        self.fd.close()
