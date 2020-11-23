"""
DeveloperAlbumsWindow.py
"""

import io
import yaml
from PyQt5 import QtWidgets, QtCore, QtGui

class PieceNameDialog(QtWidgets.QDialog):
    """
    Piece name dialog
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self._artist = None
        self._album = None
        self._tracks = None

        self._layout = QtWidgets.QVBoxLayout()

        self._label = QtWidgets.QLabel("Enter the name of the piece")
        self._layout.addWidget(self._label)

        self._piece_name_edit = QtWidgets.QLineEdit(self)
        self._layout.addWidget(self._piece_name_edit)

        # --- buttons ---
        self._button_layout = QtWidgets.QHBoxLayout()

        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._cancel_button.clicked.connect(self.reject)
        self._button_layout.addWidget(self._cancel_button)

        self._button_layout.addStretch()

        self._next_button = QtWidgets.QPushButton("Next")
        self._next_button.setDefault(True)
        self._next_button.clicked.connect(self.onNext)
        self._button_layout.addWidget(self._next_button)
        self._layout.addLayout(self._button_layout)

        self.setLayout(self._layout)

    def setPiece(self, artist, album, tracks):
        self._artist = artist
        self._album = album
        self._tracks = tracks

        # take the piece name from the track name, which is usally the case
        piece_name = tracks[0]['name']
        self._piece_name_edit.setText(piece_name)

        font = self._piece_name_edit.font()
        fm = QtGui.QFontMetrics(font)
        self._piece_name_edit.setFixedSize(fm.width(piece_name), fm.height())

        super().adjustSize()

    def onNext(self):
        """
        Called when clicked on 'Next' button
        """
        self.accept()

        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        if file_name[0]:
            track_ids = []
            for track in self._tracks:
                track_ids.append(track['id'])

            obj = {
                "composer_id": self._artist['id'],
                "name": self._piece_name_edit.text(),
                "album_id": self._album['id'],
                "tracks": track_ids
            }

            with io.open(file_name[0], 'w', encoding = 'utf8') as outfile:
                yaml.dump(obj, outfile, default_flow_style = False, allow_unicode = True)



class DeveloperAlbumsWindow(QtWidgets.QMainWindow):
    """
    Developer window
    """

    def __init__(self):
        super().__init__()
        self._artist = None
        # Spotify object
        self._spotify = None
        self._market = None
        self._results = None
        self._settings = QtCore.QSettings()
        self._piece_name_dlg = PieceNameDialog(self)

        self.readSettings()
        self.setupWidgets()
        self.setWindowTitle("Station Developer Tool: Artist's Albums")

    def setupWidgets(self):
        """
        Setup widgets
        """
        w = QtWidgets.QWidget(self)
        w.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QVBoxLayout()

        self._artist_name = QtWidgets.QLabel("")
        layout.addWidget(self._artist_name)

        self._album_list = QtWidgets.QTreeWidget()
        self._album_list.setHeaderHidden(True)
        self._album_list.setHeaderLabels(["Name", ""])
        layout.addWidget(self._album_list)

        w.setLayout(layout)
        self.setCentralWidget(w)

        self.updateWidgets()

        self._album_list.itemExpanded.connect(self.onAlbumExpanded)

        self._save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        self._save_shortcut.activated.connect(self.onSave)

    def updateWidgets(self):
        """
        Update widgets
        """
        pass

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

        self._piece_name_dlg.setPiece(self._artist, album, tracks)
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
        self._settings.beginGroup("DeveloperAlbumsWindow")
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.endGroup()

    def readSettings(self):
        """
        Read settings
        """
        self._settings.beginGroup("DeveloperAlbumsWindow")
        geom = self._settings.value("geometry")
        if geom is None:
            screen_rc = QtWidgets.QApplication.desktop().screenGeometry()
            wnd_wd = 750
            wnd_ht = int(0.9 * screen_rc.height())
            self.setGeometry(QtCore.QRect(500, (screen_rc.height() - wnd_ht) / 2, wnd_wd, wnd_ht))
        else:
            self.restoreGeometry(geom)
        self._settings.endGroup()

    def setSpotify(self, spotify, market):
        """
        Setup spotify object
        """
        self._spotify = spotify
        self._market = market
        if spotify is None:
            return

    def setArtist(self, artist):
        """
        Set artist
        """
        self._artist = artist

        self._artist_name.setText(self._artist['name'])

        self._album_list.clear()

        self._results = self._spotify.artist_albums(self._artist['id'], album_type='album', limit=50, country=self._market)
        all_albums = self._results['items']
        # while self._results['next']:
        #     self._results = self._spotify.next(self._results)
        #     all_albums.extend(self._results['items'])

        root = self._album_list.invisibleRootItem()
        for album in all_albums:
            ti = QtWidgets.QTreeWidgetItem(root)
            ti.setText(0, album['name'])
            ti.setData(0, QtCore.Qt.UserRole, album)
            ti.setFirstColumnSpanned(True)

            empty_ti = QtWidgets.QTreeWidgetItem(ti)
            ti.addChild(empty_ti)

            self._album_list.addTopLevelItem(ti)

        for i in range(self._album_list.columnCount()):
            self._album_list.resizeColumnToContents(i)
