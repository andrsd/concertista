import os
import sys
from PyQt5 import QtGui


class Assets:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.on_new()
        return cls._instance

    def on_new(self):
        if getattr(sys, 'frozen', False):
            path = sys._MEIPASS
        else:
            path = os.path.dirname(__file__)

        self.music_dir = os.path.join(path, 'music')

        icons_dir = os.path.join(path, 'icons')
        self.author_icon = QtGui.QIcon(os.path.join(icons_dir, "author.svg"))
        self.piece_icon = QtGui.QIcon(os.path.join(icons_dir, "vinyl.svg"))
        self.prev_icon = QtGui.QIcon(os.path.join(icons_dir, "prev.svg"))
        self.next_icon = QtGui.QIcon(os.path.join(icons_dir, "next.svg"))
        self.play_icon = QtGui.QIcon(os.path.join(icons_dir, "play.svg"))
        self.pause_icon = QtGui.QIcon(os.path.join(icons_dir, "pause.svg"))

        self.spotify_logo = QtGui.QIcon(os.path.join(icons_dir, "spotify-logo.svg"))
