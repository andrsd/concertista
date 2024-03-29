"""
MainWindow.py
"""

import sys
import random
import platform
from PyQt5 import QtWidgets, QtCore, QtNetwork, QtGui
from concertista import server
from concertista.assets import Assets
from concertista.DB import DB
from concertista.AboutDialog import AboutDialog
from concertista.StationSearchDialog import StationSearchDialog
from concertista.PreferencesWindow import PreferencesWindow
from concertista.DeveloperWindow import DeveloperWindow

if platform.system() == "Darwin":
    WINDOW_TITLE = "Player"
else:
    WINDOW_TITLE = "Concertista"


class MainWindow(QtWidgets.QMainWindow):
    """
    Main window
    """

    ALBUM_IMAGE_WD = 128
    ALBUM_IMAGE_HT = 128

    VOLUME_PAGE_STEP = 5
    VOLUME_MINIMUM = 0
    VOLUME_MAXIMUM = 100

    # delay in milliseconds for updating player status (assumes good connection
    # to Spotify)
    UPDATE_DELAY_MS = 500

    def __init__(self):
        super().__init__()
        random.seed()
        # database
        self._db = DB()
        self.loadDB()
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
        self._current_title = ""
        self._current_artists = []
        self._volume = None
        self._settings = QtCore.QSettings()
        self._about_dlg = None
        self._preferences_window = PreferencesWindow(self._db, self)
        self._preferences_window.preferencesUpdated.connect(
            self.onPreferencesUpdated)
        self._developer_window = None
        self._window_menu = None
        self._show_prefs_window = None

        self._station_search_dlg = StationSearchDialog(self._db, self)
        self._station_search_dlg.accepted.connect(self.onStationSearchPlay)

        server.signaler.connectToSpotify.connect(self.setupSpotify)

        self._nam = QtNetwork.QNetworkAccessManager()
        self._nam.finished.connect(self.onNetworkReply)

        self.readSettings()
        self.setWindowTitle(WINDOW_TITLE)
        self.setupWidgets()
        self.setupMenuBar()
        self.updateMenuBar()

    def setupWidgets(self):
        """
        Setup widgets
        """
        w = QtWidgets.QWidget(self)
        w.setContentsMargins(0, 0, 0, 0)

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
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)

        self._spotify_logo = QtWidgets.QLabel()
        self._spotify_logo.setPixmap(Assets().spotify_logo.pixmap(80, 24))
        top_layout.addWidget(self._spotify_logo)

        top_layout.addSpacing(8)

        self._title = QtWidgets.QLabel("")
        font = self._title.font()
        font.setBold(True)
        self._title.setFont(font)
        self._title.setAlignment(QtCore.Qt.AlignLeft)
        self._title.setMinimumWidth(440)
        top_layout.addWidget(self._title)

        self._artists = QtWidgets.QLabel("")
        font = self._artists.font()
        font.setPointSize(int(0.95 * font.pointSize()))
        self._artists.setFont(font)
        self._artists.setAlignment(QtCore.Qt.AlignLeft)
        self._artists.setMinimumWidth(440)
        top_layout.addWidget(self._artists)

        top_layout.addStretch()

        bottom_h_layout = QtWidgets.QHBoxLayout()

        button_h_layout = QtWidgets.QHBoxLayout()
        button_h_layout.setContentsMargins(0, 0, 0, 0)
        button_h_layout.setSpacing(4)

        self._prev_button = QtWidgets.QPushButton()
        self._prev_button.setIcon(Assets().prev_icon)
        self._prev_button.setIconSize(QtCore.QSize(32, 32))
        self._prev_button.setFixedSize(QtCore.QSize(32, 32))
        self._prev_button.setStyleSheet("QPushButton {border:none}")
        self._prev_button.setEnabled(False)
        button_h_layout.addWidget(self._prev_button)

        self._play_pause_button = QtWidgets.QPushButton()
        self._play_pause_button.setIcon(Assets().play_icon)
        self._play_pause_button.setIconSize(QtCore.QSize(32, 32))
        self._play_pause_button.setFixedSize(QtCore.QSize(32, 32))
        self._play_pause_button.setStyleSheet("QPushButton {border:none}")
        self._play_pause_button.setEnabled(False)
        button_h_layout.addWidget(self._play_pause_button)

        self._next_button = QtWidgets.QPushButton()
        self._next_button.setIcon(Assets().next_icon)
        self._next_button.setIconSize(QtCore.QSize(32, 32))
        self._next_button.setFixedSize(QtCore.QSize(32, 32))
        self._next_button.setStyleSheet("QPushButton {border:none}")
        self._next_button.setEnabled(False)
        button_h_layout.addWidget(self._next_button)

        bottom_h_layout.addLayout(button_h_layout)

        bottom_h_layout.addSpacing(10)

        self._volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._volume_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self._volume_slider.setTracking(True)
        self._volume_slider.setMinimum(self.VOLUME_MINIMUM)
        self._volume_slider.setMaximum(self.VOLUME_MAXIMUM)
        self._volume_slider.setPageStep(self.VOLUME_PAGE_STEP)
        bottom_h_layout.addWidget(self._volume_slider)

        bottom_h_layout.addSpacing(15)

        self._device_combo_box = QtWidgets.QComboBox()
        bottom_h_layout.addWidget(self._device_combo_box)

        bottom_h_layout.setContentsMargins(0, 0, 0, 0)

        top_layout.addLayout(bottom_h_layout)

        self._top_pane.setLayout(top_layout)

        layout.addWidget(self._top_pane)

        h_layout.addLayout(layout)

        w.setLayout(h_layout)
        self.setCentralWidget(w)
        self.setMaximumHeight(self.ALBUM_IMAGE_HT + 24)

        self._device_combo_box.setEnabled(False)
        self._volume_slider.setEnabled(False)

        self._prev_button.clicked.connect(self.onPrevious)
        self._play_pause_button.clicked.connect(self.onPlayPause)
        self._next_button.clicked.connect(self.onNext)

        self._device_combo_box.currentIndexChanged.connect(
            self.onCurrentDeviceChanged)
        self._volume_slider.valueChanged.connect(self.onVolumeChanged)

    def setupMenuBar(self):
        """
        Setup menu bar
        """
        self._menubar = QtWidgets.QMenuBar(self)

        self._station_menu = self._menubar.addMenu("Station")
        self._new_station = self._station_menu.addAction(
            "New", self.onNewStation, "Ctrl+N")
        self._station_search = self._station_menu.addAction(
            "Search...", self.onStationSearch, "Ctrl+F")

        self._dev_separator = self._station_menu.addSeparator()
        self._developer = self._station_menu.addAction(
            "Developer...", self.onDeveloper, "Ctrl+Alt+I")

        # The "About" item is fine here, since we assume Mac and that will
        # place the item into  different submenu but this will need to be fixed
        # for linux and windows
        self._station_menu.addSeparator()
        self._preferences_action = self._station_menu.addAction(
            "Preferences...", self.onPreferences)
        self._about_box_action = self._station_menu.addAction(
            "About...", self.onAbout)

        if platform.system() != "Darwin":
            self._station_menu.addSeparator()
            self._quit_action = self._station_menu.addAction(
                "Quit", self.close, "Ctrl+Q")

        self._controls_menu = self._menubar.addMenu("Controls")
        self._play_pause = self._controls_menu.addAction(
            "Play", self.onPlayPause, "Space")
        self._next = self._controls_menu.addAction(
            "Next", self.onNext, "Ctrl+Right")
        self._previous = self._controls_menu.addAction(
            "Previous", self.onPrevious, "Ctrl+Left")
        self._controls_menu.addSeparator()
        self._volume_up = self._controls_menu.addAction(
            "Increase Volume", self.onVolumeUp, "Ctrl+Up")
        self._volume_down = self._controls_menu.addAction(
            "Decrease Volume", self.onVolumeDown, "Ctrl+Down")
        self._controls_menu.addSeparator()

        if platform.system() == "Darwin":
            self._window_menu = self._menubar.addMenu("Window")
            self._minimize = self._window_menu.addAction(
                "Minimize", self.onMinimize, "Ctrl+M")
            self._window_menu.addSeparator()
            self._bring_all_to_front = self._window_menu.addAction(
                "Bring All to Front", self.onBringAllToFront)

            self._window_menu.addSeparator()
            self._show_main_window = self._window_menu.addAction(
                "Player", self.onShowMainWindow)
            self._show_main_window.setCheckable(True)

            self._show_prefs_window = self._window_menu.addAction(
                '\u200C' + "Preferences", self.onShowPreferences)
            self._show_prefs_window.setCheckable(True)
            self._show_prefs_window.setVisible(False)
            self._preferences_window.window_action = self._show_prefs_window

            self._action_group_windows = QtWidgets.QActionGroup(self)
            self._action_group_windows.addAction(self._show_main_window)
            self._action_group_windows.addAction(self._show_prefs_window)

        self.setMenuBar(self._menubar)

    def updateMenuBar(self):
        """
        Update menu bar
        """
        if self._window_menu is not None:
            qapp = QtWidgets.QApplication.instance()
            active_window = qapp.activeWindow()
            if active_window == self:
                self._show_main_window.setChecked(True)
            elif active_window == self._preferences_window:
                self._show_prefs_window.setChecked(True)

        visible = self._preferences_window.show_developer.isChecked()
        self._dev_separator.setVisible(visible)
        self._developer.setVisible(visible)

    def randomizePieces(self, piece_ids):
        """
        Randomize list of pieces
        """
        rng = random.sample(piece_ids, k=len(piece_ids))
        pieces = self._db.get_pieces()

        # if avg. track length is 5 mins, then this will be about 16 hours of
        # music
        max_tracks = 200
        uris = []
        for id in rng:
            piece = pieces[id]
            for track in piece['tracks']:
                uri = "spotify:track:{}".format(track)
                uris.append(uri)
                max_tracks = max_tracks - 1
            if max_tracks <= 0:
                break
        return uris

    def onNewStation(self):
        """
        Start to listen to new music
        """
        if self._active_device_id is not None:
            pieces = {}
            if (self._preferences_window.music_library.checkedId() ==
                    PreferencesWindow.MUSIC_LIBRARY_ENTIRE):
                pieces = self._db.get_pieces()
            else:
                pieces = self._preferences_window.user_selection

            if len(pieces) > 0:
                uris = self.randomizePieces(list(pieces.keys()))
                self._spotify.start_playback(
                    device_id=self._active_device_id,
                    uris=uris)
        else:
            self.reportUnknownDeviceId()

    def onStationSearch(self):
        """
        Open the new station from search dialog
        """
        self._station_search_dlg.open()

    def onStationSearchPlay(self):
        """
        Start playing pieces according to a search
        """
        if self._active_device_id is not None:
            type = self._station_search_dlg.db_item['type']
            id = self._station_search_dlg.db_item['id']
            if type == 'piece':
                uris = self.randomizePieces([id])
                self._spotify.start_playback(
                    device_id=self._active_device_id,
                    uris=uris)
            elif type == 'composer':
                piece_ids = self._db.get_composer_pieces(id)
                uris = self.randomizePieces(piece_ids)
                self._spotify.start_playback(
                    device_id=self._active_device_id,
                    uris=uris)
        else:
            self.reportUnknownDeviceId()

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
        if cpb['is_playing'] is True:
            self._spotify.pause_playback(device_id=self._active_device_id)
            self._play_pause.setText("Play")
            self._play_pause_button.setIcon(Assets().play_icon)
        else:
            self._spotify.start_playback(device_id=self._active_device_id)
            self._play_pause.setText("Pause")
            self._play_pause_button.setIcon(Assets().pause_icon)

    def onNext(self):
        """
        Skip to the next track
        """
        self._spotify.next_track(device_id=self._active_device_id)
        QtCore.QTimer.singleShot(
            self.UPDATE_DELAY_MS, self.updateCurrentlyPlaying)

    def onPrevious(self):
        """
        Jump to the previous track
        """
        self._spotify.previous_track(device_id=self._active_device_id)
        QtCore.QTimer.singleShot(
            self.UPDATE_DELAY_MS, self.updateCurrentlyPlaying)

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
        """
        Called when volume was changed
        """
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

    def onShowPreferences(self):
        """
        Called when show preferences window action is triggered
        """
        self._preferences_window.showNormal()
        self._preferences_window.activateWindow()
        self._preferences_window.raise_()
        self.updateMenuBar()

    def onPreferences(self):
        """
        Called when 'Preferences' window is requested
        """
        if self._show_prefs_window is not None:
            self._show_prefs_window.setVisible(True)
        self._preferences_window.show()
        self.updateMenuBar()

    def onPreferencesUpdated(self):
        """
        Called when 'Preferences' are updated
        """
        self.updateMenuBar()

    def event(self, event):
        """
        Event override
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.updateMenuBar()
        return super().event(event)

    def resizeEvent(self, event):
        """
        Resize event
        """
        self.updateCurrentlyPlayingTitle()

    def closeEvent(self, event):
        """
        Called when EventClose is received
        """
        self.writeSettings()
        event.accept()
        if platform.system() != "Darwin":
            sys.exit()

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
            wnd_wd = 600
            wnd_ht = self.ALBUM_IMAGE_HT + 24
            self.setGeometry(QtCore.QRect(
                screen_rc.width() - wnd_wd - 10, 10,
                wnd_wd, wnd_ht))
        else:
            self.restoreGeometry(geom)
        self._settings.endGroup()

    def connectToSpotify(self):
        """
        Connect to Spotify via our local HTTP server
        """
        spotify_req = QtNetwork.QNetworkRequest(
            QtCore.QUrl("http://localhost:{}".format(server.port)))
        self._nam.get(spotify_req)

    def setupSpotify(self, spotify):
        """
        Link Spotify information to our internal data
        """
        self._spotify = spotify
        if spotify is None:
            return

        self._me = self._spotify.me()

        # get active playback device and save its state
        devs = self._spotify.devices()
        self._devices = []
        for d in devs['devices']:
            self._devices.append(d)
            if d['is_active'] is True:
                self._active_device_id = d['id']
                self._volume = d['volume_percent']

        self.updateCurrentlyPlaying()

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

        self._prev_button.setEnabled(True)
        self._play_pause_button.setEnabled(True)
        self._next_button.setEnabled(True)

        self._device_combo_box.setEnabled(True)
        self._volume_slider.setEnabled(True)

    def updateCurrentlyPlayingTitle(self):
        """
        Update title and artists of currently playing track
        """
        title = self._current_title
        metrics = QtGui.QFontMetrics(self._title.font())
        text = metrics.elidedText(
            title, QtCore.Qt.ElideRight, self._title.width())
        self._title.setText(text)

        artists = ", ".join(self._current_artists)
        metrics = QtGui.QFontMetrics(self._artists.font())
        text = metrics.elidedText(
            artists, QtCore.Qt.ElideRight, self._artists.width())
        self._artists.setText(text)

    def updateCurrentlyPlaying(self):
        """
        Update information of currenlty playing track
        """
        cpb = self._spotify.current_playback()
        if cpb is not None:
            if cpb['is_playing'] is True:
                self._play_pause.setText("Pause")
                self._play_pause_button.setIcon(Assets().pause_icon)
            else:
                self._play_pause.setText("Play")
                self._play_pause_button.setIcon(Assets().play_icon)

            if ('item' in cpb) and (cpb['item'] is not None):
                self._current_title = cpb['item']['name']
                self._current_artists = []
                for a in cpb['item']['artists']:
                    self._current_artists.append(a['name'])
                self.updateCurrentlyPlayingTitle()

                images = cpb['item']['album']['images']
                for img in images:
                    if (img['height'] >= self.ALBUM_IMAGE_HT and
                            img['height'] <= 600):
                        img_url = img['url']

                img_req = QtNetwork.QNetworkRequest(QtCore.QUrl(img_url))
                self._nam.get(img_req)

    def loadDB(self):
        """
        Load the database
        """
        self._db.load()

    def onNetworkReply(self, reply):
        """
        Called when network request was finished
        """
        if reply.url().host() == "localhost":
            # our own requests
            return
        else:
            img = QtGui.QImage()
            img.load(reply, "")
            scaled_img = img.scaledToWidth(self.ALBUM_IMAGE_WD)
            pixmap = QtGui.QPixmap.fromImage(scaled_img)
            self._image.setPixmap(pixmap)

    def reportUnknownDeviceId(self):
        """
        Show message box reporting unknown device ID
        """
        mb = QtWidgets.QMessageBox(self)
        mb.setIcon(QtWidgets.QMessageBox.Critical)
        mb.setWindowTitle("Error")
        mb.addButton(QtWidgets.QMessageBox.Ok)
        mb.setText("Device ID unknown")
        mb.setInformativeText(
            "Try restarting Spotify and then this application.")
        horizontalSpacer = QtWidgets.QSpacerItem(
            400, 0,
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout = mb.layout()
        layout.addItem(
            horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
        mb.exec()
