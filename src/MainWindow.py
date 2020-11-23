"""
MainWindow.py
"""

import os
import io
import yaml
import random
from PyQt5 import QtWidgets, QtCore
import consts
from AboutDialog import AboutDialog
from DeveloperWindow import DeveloperWindow

class MainWindow(QtWidgets.QMainWindow):
    """
    Main window
    """

    def __init__(self):
        super().__init__()
        # database
        self._db = None
        # market for spotify
        self._market = 'US'
        # Spotify object
        self._spotify = None
        # my Spotify profile
        self._me = None
        # Spotify devices
        self._devices = None
        # active Spotify device Id
        self._active_device_id = None
        self._settings = QtCore.QSettings()
        self._about_dlg = None
        self._developer_window = None

        self.readSettings()
        self.setupWidgets()
        self.setupMenuBar()
        self.updateMenuBar()

    def setupWidgets(self):
        """
        Setup widgets
        """
        w = QtWidgets.QWidget(self)
        w.setContentsMargins(0, 0, 0 ,0)
        layout = QtWidgets.QVBoxLayout()

        self.top_pane = QtWidgets.QWidget(self)
        self.top_pane.setFixedHeight(200)

        top_layout = QtWidgets.QVBoxLayout()

        self.title = QtWidgets.QLabel("")
        font = self.title.font()
        font.setBold(True)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        top_layout.addWidget(self.title)

        self.artists = QtWidgets.QLabel("")
        font = self.artists.font()
        font.setPointSize(int(0.95 * font.pointSize()))
        self.artists.setFont(font)
        self.artists.setAlignment(QtCore.Qt.AlignLeft)
        top_layout.addWidget(self.artists)

        top_layout.addStretch()

        self.top_pane.setLayout(top_layout)

        layout.addWidget(self.top_pane)

        w.setLayout(layout)
        self.setCentralWidget(w)

    def setupMenuBar(self):
        """
        Setup menu bar
        """
        self.menubar = QtWidgets.QMenuBar(self)

        self.station_menu = self.menubar.addMenu("Station")
        self._new_station = self.station_menu.addAction("New", self.onNewStation, "Ctrl+N")
        self.station_menu.addSeparator()
        self._developer = self.station_menu.addAction("Developer", self.onDeveloper, "Ctrl+Alt+I")

        # The "About" item is fine here, since we assume Mac and that will place the item into
        # different submenu but this will need to be fixed for linux and windows
        self.station_menu.addSeparator()
        self._about_box_action = self.station_menu.addAction("About", self.onAbout)

        self.controls_menu = self.menubar.addMenu("Controls")
        self._play_pause = self.controls_menu.addAction("Play", self.onPlayPause, "Space")
        self._next = self.controls_menu.addAction("Next", self.onNext, "Ctrl+Right")
        self._previous = self.controls_menu.addAction("Previous", self.onPrevious, "Ctrl+Left")
        self.controls_menu.addSeparator()
        self._volume_up = self.controls_menu.addAction("Increase Volume", self.onVolumeUp, "Ctrl+Up")
        self._volume_down = self.controls_menu.addAction("Decrease Volume", self.onVolumeDown, "Ctrl+Down")
        self.controls_menu.addSeparator()

        self.window_menu = self.menubar.addMenu("Window")
        self._minimize = self.window_menu.addAction("Minimize", self.onMinimize, "Ctrl+M")
        self.window_menu.addSeparator()
        self._bring_all_to_front = self.window_menu.addAction("Bring All to Front",
            self.onBringAllToFront)

        self.window_menu.addSeparator()
        self._show_main_window = self.window_menu.addAction("Spotify Classical Radio", self.onShowMainWindow)
        self._show_main_window.setCheckable(True)

        self.action_group_windows = QtWidgets.QActionGroup(self)
        self.action_group_windows.addAction(self._show_main_window)

        self.setMenuBar(self.menubar)

    def updateMenuBar(self):
        """
        Update menu bar
        """
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self:
            self._show_main_window.setChecked(True)

    def onNewStation(self):
        """
        Start to listen to new music
        """
        pieces = self._db.get_pieces()
        rng = random.sample(list(pieces.keys()), k = 3)

        # add the tracks
        max_tracks = 200
        uris = []
        for id in rng:
            piece = pieces[id]
            for track in piece['tracks']:
                uri = "spotify:track:{}".format(track)
                uris.append(uri)
                max_tracks = max_tracks - 1
                if max_tracks == 0:
                    break
            if max_tracks == 0:
                break
        self._spotify.start_playback(device_id=self._active_device_id, uris=uris)

    def onDeveloper(self):
        """
        Open developer GUI
        """
        if self._developer_window is None:
            self._developer_window = DeveloperWindow()
            self._developer_window.setupSpotify(self._spotify, self._market)
        self._developer_window.show()

    def onPlayPause(self):
        """
        Start/Pause the playback
        """
        cpb = self._spotify.current_playback()
        if cpb['is_playing'] == True:
            self._spotify.pause_playback(device_id=self._active_device_id)
            self._play_pause.setText("Play")
        else:
            self._spotify.start_playback(device_id=self._active_device_id)
            self._play_pause.setText("Pause")

    def onNext(self):
        """
        Skip to the next track
        """
        self._spotify.next_track(device_id=self._active_device_id)

    def onPrevious(self):
        """
        Jump to the previous track
        """
        self._spotify.previous_track(device_id=self._active_device_id)

    def onVolumeUp(self):
        """
        Increase volume
        """
        self._volume = min(self._volume + 5, 100)
        self._spotify.volume(self._volume, device_id=self._active_device_id)

    def onVolumeDown(self):
        """
        Decrease volume
        """
        self._volume = max(self._volume - 5, 0)
        self._spotify.volume(self._volume, device_id=self._active_device_id)

    def onAbout(self):
        """
        Called when FileAbout action is triggered
        """
        if self._about_dlg is None:
            self._about_dlg = AboutDialog(self)
        self._about_dlg.show()

    def onMinimize(self):
        """
        Called when WindowMinimize is triggered
        """
        self.showMinimized()

    def onBringAllToFront(self):
        """
        Called when WindowBringAllToFront is triggered
        """
        self.showNormal()

    def onShowMainWindow(self):
        """
        Called when show main window is triggered
        """
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.updateMenuBar()

    def event(self, event):
        """
        Event override
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        """
        Called when EventClose is recieved
        """
        self.writeSettings()
        event.accept()

    def writeSettings(self):
        """
        Write settings
        """
        self._settings.beginGroup("MainWindow")
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.endGroup()

    def readSettings(self):
        """
        Read settings
        """
        self._settings.beginGroup("MainWindow")
        geom = self._settings.value("geometry")
        if geom is None:
            screen_rc = QtWidgets.QApplication.desktop().screenGeometry()
            wnd_wd = 450
            wnd_ht = int(0.9 * screen_rc.height())
            self.setGeometry(QtCore.QRect(screen_rc.width() - wnd_wd - 10, (screen_rc.height() - wnd_ht) / 2, wnd_wd, wnd_ht))
        else:
            self.restoreGeometry(geom)
        self._settings.endGroup()

    def setupSpotify(self, spotify):
        self._spotify = spotify
        if spotify is None:
            return

        self._me = self._spotify.me()

        # get active playback device and save its state
        devs = self._spotify.devices()
        self._devices = []
        for d in devs['devices']:
            self._devices.append(d)
            if d['is_active'] == True:
                self._active_device_id = d['id']
                self._volume = d['volume_percent']

        cpb = self._spotify.current_playback()
        if cpb is not None:
            if cpb['is_playing'] == True:
                self._play_pause.setText("Pause")
            else:
                self._play_pause.setText("Play")

            # set current playing track
            self.title.setText(cpb['item']['name'])
            artists = []
            for a in cpb['item']['artists']:
                artists.append(a['name'])
            self.artists.setText(", ".join(artists))

        # fill in upcoming track
        # queue = self._spotify.current_playback()

    def setupDB(self, db):
        """
        Setup the database object
        """
        self._db = db
