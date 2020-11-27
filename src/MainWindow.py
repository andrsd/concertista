"""
MainWindow.py
"""

import os
import io
import yaml
import random
from PyQt5 import QtWidgets, QtCore, QtNetwork, QtGui
import consts
from AboutDialog import AboutDialog
from StationByComposerDialog import StationByComposerDialog
from DeveloperWindow import DeveloperWindow

class MainWindow(QtWidgets.QMainWindow):
    """
    Main window
    """

    ALBUM_IMAGE_WD = 128
    ALBUM_IMAGE_HT = 128

    VOLUME_PAGE_STEP = 5
    VOLUME_MINIMUM = 0
    VOLUME_MAXIMUM = 100

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

        self._station_by_composer_dlg = StationByComposerDialog(self)
        self._station_by_composer_dlg.finished.connect(self.onNewStationByComposerPlay)

        self._nam = QtNetwork.QNetworkAccessManager()
        self._nam.finished.connect(self.onNetworkReply)

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

        h_layout = QtWidgets.QHBoxLayout()

        left_layout = QtWidgets.QVBoxLayout()

        self._image = QtWidgets.QLabel()
        self._image.setFixedSize(self.ALBUM_IMAGE_WD, self.ALBUM_IMAGE_HT)

        left_layout.addWidget(self._image)
        left_layout.setAlignment(QtCore.Qt.AlignTop)

        h_layout.addLayout(left_layout)

        layout = QtWidgets.QVBoxLayout()

        self._top_pane = QtWidgets.QWidget(self)

        top_layout = QtWidgets.QVBoxLayout()
        top_layout.setContentsMargins(0, 0, 0 ,0)

        self._title = QtWidgets.QLabel("")
        font = self._title.font()
        font.setBold(True)
        self._title.setFont(font)
        self._title.setAlignment(QtCore.Qt.AlignLeft)
        top_layout.addWidget(self._title)

        self._artists = QtWidgets.QLabel("")
        font = self._artists.font()
        font.setPointSize(int(0.95 * font.pointSize()))
        self._artists.setFont(font)
        self._artists.setAlignment(QtCore.Qt.AlignLeft)
        top_layout.addWidget(self._artists)

        top_layout.addStretch()

        bottom_h_layout = QtWidgets.QHBoxLayout()
        self._volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._volume_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self._volume_slider.setTracking(True)
        self._volume_slider.setMinimum(self.VOLUME_MINIMUM)
        self._volume_slider.setMaximum(self.VOLUME_MAXIMUM)
        self._volume_slider.setPageStep(self.VOLUME_PAGE_STEP)
        bottom_h_layout.addWidget(self._volume_slider)

        self._device_combo_box = QtWidgets.QComboBox()
        bottom_h_layout.addWidget(self._device_combo_box)
        bottom_h_layout.setContentsMargins(0, 0, 0 ,0)

        top_layout.addLayout(bottom_h_layout)

        self._top_pane.setLayout(top_layout)

        layout.addWidget(self._top_pane)

        h_layout.addLayout(layout)

        w.setLayout(h_layout)
        self.setCentralWidget(w)

        self._device_combo_box.currentIndexChanged.connect(self.onCurrentDeviceChanged)
        self._volume_slider.valueChanged.connect(self.onVolumeChanged)

    def setupMenuBar(self):
        """
        Setup menu bar
        """
        self._menubar = QtWidgets.QMenuBar(self)

        self._station_menu = self._menubar.addMenu("Station")
        self._new_station = self._station_menu.addAction("New", self.onNewStation, "Ctrl+N")
        self._new_station_by_composer = self._station_menu.addAction("By composer", self.onNewStationByComposer)
        self._station_menu.addSeparator()
        self._developer = self._station_menu.addAction("Developer", self.onDeveloper, "Ctrl+Alt+I")

        # The "About" item is fine here, since we assume Mac and that will place the item into
        # different submenu but this will need to be fixed for linux and windows
        self._station_menu.addSeparator()
        self._about_box_action = self._station_menu.addAction("About", self.onAbout)

        self._controls_menu = self._menubar.addMenu("Controls")
        self._play_pause = self._controls_menu.addAction("Play", self.onPlayPause, "Space")
        self._next = self._controls_menu.addAction("Next", self.onNext, "Ctrl+Right")
        self._previous = self._controls_menu.addAction("Previous", self.onPrevious, "Ctrl+Left")
        self._controls_menu.addSeparator()
        self._volume_up = self._controls_menu.addAction("Increase Volume", self.onVolumeUp, "Ctrl+Up")
        self._volume_down = self._controls_menu.addAction("Decrease Volume", self.onVolumeDown, "Ctrl+Down")
        self._controls_menu.addSeparator()

        self._window_menu = self._menubar.addMenu("Window")
        self._minimize = self._window_menu.addAction("Minimize", self.onMinimize, "Ctrl+M")
        self._window_menu.addSeparator()
        self._bring_all_to_front = self._window_menu.addAction("Bring All to Front",
            self.onBringAllToFront)

        self._window_menu.addSeparator()
        self._show_main_window = self._window_menu.addAction("Spotify Classical Radio", self.onShowMainWindow)
        self._show_main_window.setCheckable(True)

        self._action_group_windows = QtWidgets.QActionGroup(self)
        self._action_group_windows.addAction(self._show_main_window)

        self.setMenuBar(self._menubar)

    def updateMenuBar(self):
        """
        Update menu bar
        """
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self:
            self._show_main_window.setChecked(True)

    def randomizePiecesAndPlay(self, piece_ids):
        """
        Randomize list of pieces and start playing
        """
        rng = random.sample(piece_ids, k = 3)
        pieces = self._db.get_pieces()

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

    def onNewStation(self):
        """
        Start to listen to new music
        """
        pieces = self._db.get_pieces()
        self.randomizePiecesAndPlay(list(pieces.keys()))

    def onNewStationByComposer(self):
        """
        Open the new station using composer name dialog
        """
        self._station_by_composer_dlg.open()

    def onNewStationByComposerPlay(self):
        """
        Start playing pieces from a composer
        """
        composer_id = self._station_by_composer_dlg._artist["id"]
        pieces_ids = self._db.get_composer_pieces(composer_id)
        self.randomizePiecesAndPlay(pieces_ids)

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
        volume = min(self._volume + self.VOLUME_PAGE_STEP, self.VOLUME_MAXIMUM)
        self._volume_slider.setValue(volume)

    def onVolumeDown(self):
        """
        Decrease volume
        """
        volume = max(self._volume - self.VOLUME_PAGE_STEP, self.VOLUME_MINIMUM)
        self._volume_slider.setValue(volume)

    def onVolumeChanged(self, value):
        self._volume = value
        self._spotify.volume(self._volume, device_id=self._active_device_id)

    def onAbout(self):
        """
        Called when FileAbout action is triggered
        """
        if self._about_dlg is None:
            self._about_dlg = AboutDialog(self)
        self._about_dlg.show()

    def onCurrentDeviceChanged(self, index):
        """
        When current device changes
        """
        new_device_id = self._device_combo_box.itemData(index)
        if new_device_id != self._active_device_id:
            self._active_device_id = self._device_combo_box.itemData(index)
            self._spotify.transfer_playback(self._active_device_id)

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

        self._settings.setValue("device", self._device_combo_box.currentData())

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
            self._title.setText(cpb['item']['name'])
            artists = []
            for a in cpb['item']['artists']:
                artists.append(a['name'])
            self._artists.setText(", ".join(artists))

        images = cpb['item']['album']['images']
        for img in images:
            if (img['height'] >= self.ALBUM_IMAGE_HT) and (img['height'] <= 600):
                img_url = img['url']

        img_req = QtNetwork.QNetworkRequest(QtCore.QUrl(img_url))
        self._nam.get(img_req)

        # fill in upcoming track
        # queue = self._spotify.current_playback()

        # devices
        self._device_combo_box.blockSignals(True)
        for dev in self._devices:
            self._device_combo_box.addItem(dev['name'], dev['id'])
        self._device_combo_box.blockSignals(False)

        if self._active_device_id is None:
            active_device = self._settings.value("device")
            if active_device is not None:
                index = self._device_combo_box.findData(active_device)
                if index != -1:
                    self._device_combo_box.setCurrentIndex(index)
        else:
            index = self._device_combo_box.findData(self._active_device_id)
            if index != -1:
                self._device_combo_box.setCurrentIndex(index)

        # volume
        if self._volume is None:
            pass
        else:
            self._volume_slider.blockSignals(True)
            self._volume_slider.setValue(self._volume)
            self._volume_slider.blockSignals(False)

    def setupDB(self, db):
        """
        Setup the database object
        """
        self._db = db
        self._station_by_composer_dlg.setupDB(db)

    def onNetworkReply(self, reply):
        """
        Called when network request was finished
        """
        img = QtGui.QImage()
        img.load(reply, "")
        # img.scaled(self.ALBUM_IMAGE_WD, self.ALBUM_IMAGE_HT, QtCore.Qt.KeepAspectRatio)
        # img.scaled(self.ALBUM_IMAGE_WD, self.ALBUM_IMAGE_HT)
        scaled_img = img.scaledToWidth(self.ALBUM_IMAGE_WD)
        pixmap = QtGui.QPixmap.fromImage(scaled_img)
        self._image.setPixmap(pixmap)
