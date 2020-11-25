"""
DeveloperWindow.py
"""

import yaml
from PyQt5 import QtWidgets, QtCore, QtGui
from DeveloperAlbumsWindow import DeveloperAlbumsWindow
from PieceNameDialog import PieceNameDialog

class DeveloperWindow(QtWidgets.QMainWindow):
    """
    Developer window
    """

    def __init__(self):
        super().__init__()
        # Spotify object
        self._spotify = None
        self._market = None
        self._settings = QtCore.QSettings()
        self._albums_window = None
        self._piece_name_dlg = PieceNameDialog(self)

        self.readSettings()
        self.setupWidgets()
        self.setWindowTitle("Station Developer Tool")

    def setupWidgets(self):
        """
        Setup widgets
        """
        self._tab = QtWidgets.QTabWidget(self)
        self.setContentsMargins(12, 12, 12, 10)

        # album tab
        album_tab = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)

        pane = QtWidgets.QWidget(self)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self._album_search_box = QtWidgets.QLineEdit("")
        self._album_search_box.setPlaceholderText("Album name...")
        self._album_search_box.setClearButtonEnabled(True)
        top_layout.addWidget(self._album_search_box)

        self._album_search_button = QtWidgets.QPushButton("Search")
        top_layout.addWidget(self._album_search_button)

        pane.setLayout(top_layout)

        layout.addWidget(pane)

        self._album_list = QtWidgets.QTreeWidget()
        self._album_list.setHeaderLabels(["Album", "Artist"])
        layout.addWidget(self._album_list)

        album_tab.setLayout(layout)
        self._tab.addTab(album_tab, "By Album")

        # composer tab
        composer_tab = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)

        pane = QtWidgets.QWidget(self)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self._composer_search_box = QtWidgets.QLineEdit("")
        self._composer_search_box.setPlaceholderText("Composer...")
        self._composer_search_box.setClearButtonEnabled(True)
        top_layout.addWidget(self._composer_search_box)

        self._composer_search_button = QtWidgets.QPushButton("Search")
        top_layout.addWidget(self._composer_search_button)

        pane.setLayout(top_layout)

        layout.addWidget(pane)

        self._composer_list = QtWidgets.QTreeWidget()
        self._composer_list.setHeaderLabels(["Artist", "Genres", "Popularity"])
        layout.addWidget(self._composer_list)

        composer_tab.setLayout(layout)
        self._tab.addTab(composer_tab, "By Composer")

        self.setCentralWidget(self._tab)

        self.updateWidgets()

        self._search_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self)
        self._search_shortcut.activated.connect(self.onCtrlReturn)

        self._composer_search_button.clicked.connect(self.onSearchComposer)
        self._composer_search_box.textChanged.connect(self.updateWidgets)
        self._composer_list.itemDoubleClicked.connect(self.onComposerListDoubleClicked)

        self._album_search_button.clicked.connect(self.onSearchAlbum)
        self._album_search_box.textChanged.connect(self.updateWidgets)
        self._album_list.itemExpanded.connect(self.onAlbumExpanded)

        self._save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        self._save_shortcut.activated.connect(self.onSave)

    def updateWidgets(self):
        """
        Update widgets
        """
        srch_str = self._composer_search_box.text()
        self._composer_search_button.setEnabled(len(srch_str) > 0)

    def onCtrlReturn(self):
        """
        Called then user presses Ctrl+Return
        """
        if self._tab.currentIndex() == 0:
            self._album_search_button.animateClick()
        elif self._tab.currentIndex() == 1:
            self._composer_search_button.animateClick()

    def onSearchComposer(self):
        """
        Called when search for a composer is requested
        """
        self._composer_list.clear()

        srch_str = self._composer_search_box.text()
        res = self._spotify.search(srch_str, limit=50, type='artist', market=self._market)

        root = self._composer_list.invisibleRootItem()
        for artist in res['artists']['items']:
            ti = QtWidgets.QTreeWidgetItem(root)
            ti.setText(0, artist['name'])
            ti.setData(0, QtCore.Qt.UserRole, artist)

            ti.setText(1, ", ".join(artist['genres']))

            ti.setText(2, str(artist['popularity']))

            self._composer_list.addTopLevelItem(ti)

        for i in range(self._composer_list.columnCount()):
            self._composer_list.resizeColumnToContents(i)

    def onComposerListDoubleClicked(self, item, column):
        artist = item.data(0, QtCore.Qt.UserRole)

        if self._albums_window is None:
            self._albums_window = DeveloperAlbumsWindow()
            self._albums_window.setSpotify(self._spotify, self._market)

        self._albums_window.setArtist(artist)
        self._albums_window.show()

    def onSearchAlbum(self):
        """
        Called when search for an album is requested
        """
        self._album_list.clear()

        srch_str = self._album_search_box.text()
        res = self._spotify.search(srch_str, limit=50, type='album', market=self._market)

        root = self._album_list.invisibleRootItem()
        for album in res['albums']['items']:
            ti = QtWidgets.QTreeWidgetItem(root)
            ti.setText(0, album['name'])
            ti.setData(0, QtCore.Qt.UserRole, album)

            artists = []
            for artist in album['artists']:
                artists.append(artist['name'])
            ti.setText(1, ", ".join(artists))

            empty_ti = QtWidgets.QTreeWidgetItem(ti)
            ti.addChild(empty_ti)

            self._album_list.addTopLevelItem(ti)

        for i in range(self._album_list.columnCount()):
            self._album_list.resizeColumnToContents(i)

    def onAlbumExpanded(self, item):
        """
        Called when album item expanded
        """
        first_child = item.child(0)
        fch_data = first_child.data(0, QtCore.Qt.UserRole)
        if fch_data is None:
            album_data = item.data(0, QtCore.Qt.UserRole)

            album_tracks = self._spotify.album_tracks(album_data['id'])
            for track in album_tracks['items']:
                ti = QtWidgets.QTreeWidgetItem(item)
                ti.setText(0, "{:2d}. {}".format(track['track_number'], track['name']))
                ti.setData(0, QtCore.Qt.UserRole, track)
                ti.setCheckState(0, QtCore.Qt.Unchecked)
                item.addChild(ti)

            item.removeChild(first_child)

            for i in range(self._album_list.columnCount()):
                self._album_list.resizeColumnToContents(i)

    def onSave(self):
        if self._tab.currentIndex() != 0:
            return

        items = []
        tracks = []
        for item in self._album_list.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
            if item.childCount() == 0 and item.checkState(0) == QtCore.Qt.Checked:
                tracks.append(item.data(0, QtCore.Qt.UserRole))
                items.append(item)

        if len(tracks) == 0:
            return
        # TODO: make sure that all checked items come from one album

        parent_item = item.parent()
        album = parent_item.data(0, QtCore.Qt.UserRole)
        artist = album['artists'][0]

        self._piece_name_dlg.setPiece(artist, album, tracks)
        self._piece_name_dlg.open()

    def event(self, event):
        """
        Event override
        """
        # TODO: update menu bar
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
        self._settings.beginGroup("DeveloperWindow")
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.endGroup()

    def readSettings(self):
        """
        Read settings
        """
        self._settings.beginGroup("DeveloperWindow")
        geom = self._settings.value("geometry")
        if geom is None:
            screen_rc = QtWidgets.QApplication.desktop().screenGeometry()
            wnd_wd = 750
            wnd_ht = int(0.9 * screen_rc.height())
            self.setGeometry(QtCore.QRect(10, (screen_rc.height() - wnd_ht) / 2, wnd_wd, wnd_ht))
        else:
            self.restoreGeometry(geom)
        self._settings.endGroup()

    def setupSpotify(self, spotify, market):
        """
        Setup spotify object
        """
        self._spotify = spotify
        self._market = market
        if spotify is None:
            return
