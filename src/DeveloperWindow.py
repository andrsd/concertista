"""
DeveloperWindow.py
"""

import yaml
from PyQt5 import QtWidgets, QtCore, QtGui
from DeveloperAlbumsWindow import DeveloperAlbumsWindow

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

        self.readSettings()
        self.setupWidgets()
        self.setWindowTitle("Station Developer Tool")

    def setupWidgets(self):
        """
        Setup widgets
        """
        w = QtWidgets.QWidget(self)
        w.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QVBoxLayout()

        self._top_pane = QtWidgets.QWidget(self)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self._search_box = QtWidgets.QLineEdit("")
        self._search_box.setPlaceholderText("Composer...")
        self._search_box.setClearButtonEnabled(True)
        top_layout.addWidget(self._search_box)

        self._search_button = QtWidgets.QPushButton("Search")
        top_layout.addWidget(self._search_button)

        self._top_pane.setLayout(top_layout)

        layout.addWidget(self._top_pane)

        self._composer_list = QtWidgets.QTreeWidget()
        self._composer_list.setHeaderLabels(["Artist", "Genres", "Popularity"])
        layout.addWidget(self._composer_list)

        w.setLayout(layout)
        self.setCentralWidget(w)

        self.updateWidgets()

        self._search_button.clicked.connect(self.onSearchComposer)
        self._search_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self)
        self._search_shortcut.activated.connect(self.onCtrlReturn)

        self._search_box.textChanged.connect(self.updateWidgets)

        self._composer_list.itemDoubleClicked.connect(self.onComposerListDoubleClicked)

    def updateWidgets(self):
        """
        Update widgets
        """
        srch_str = self._search_box.text()
        self._search_button.setEnabled(len(srch_str) > 0)

    def onCtrlReturn(self):
        """
        Called then user presses Ctrl+Return
        """
        self._search_button.animateClick()

    def onSearchComposer(self):
        """
        Called when search for a composer is requested
        """
        self._composer_list.clear()

        srch_str = self._search_box.text()
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
