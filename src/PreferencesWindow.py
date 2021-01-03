"""
PreferencesWindow.py
"""

from PyQt5 import QtWidgets, QtCore, QtGui

class TreeProxyFilter(QtCore.QSortFilterProxyModel):
    """
    Filter tree items and show items and theirs childs matching a reg exp
    """
    def filterAcceptsRow(self, row, parent):
        index = self.sourceModel().index(row, 0, parent)

        if not index.isValid():
            return False

        if self.filterRegExp().indexIn(index.data()) != -1:
            return True

        rows = self.sourceModel().rowCount(index)
        for row in range(rows):
            if self.filterAcceptsRow(row, index):
                return True;

        return False


class PreferencesWindow(QtWidgets.QDialog):
    """
    Preferences
    """
    preferencesUpdated = QtCore.pyqtSignal()

    MUSIC_LIBRARY_ENTIRE = 0
    MUSIC_LIBRARY_PORTION = 1

    def __init__(self, db, parent = None):
        super().__init__(parent)
        self._db = db
        self.window_action = None
        # IDs of user selected pieces
        self.user_selection = {}
        self.setMinimumWidth(500)
        self.setWindowTitle("Preferences")
        self.setWindowFlags((self.windowFlags() | QtCore.Qt.CustomizeWindowHint) & ~QtCore.Qt.WindowMaximizeButtonHint)
        self._settings = QtCore.QSettings()
        self._vlayout = QtWidgets.QVBoxLayout()

        self.buildLibraryModel()

        self.setupFonts()
        self.setupWidgets()
        self.readSettings()

    def buildLibraryModel(self):
        composers = self._db.get_composers()
        pieces = self._db.get_pieces()

        self._library_model = QtGui.QStandardItemModel()
        for cid, composer in composers.items():
            ci = QtGui.QStandardItem(composer['name'])
            ci.setData(composer['id'])
            ci.setCheckable(True)
            self._library_model.appendRow(ci)

            comp_piece_ids = self._db.get_composer_pieces(cid)
            for pid in comp_piece_ids:
                piece = pieces[pid]
                pi = QtGui.QStandardItem(piece['name'])
                pi.setData(piece['id'])
                pi.setCheckable(True)
                ci.appendRow(pi)

        self._sort_library_model = TreeProxyFilter()
        self._sort_library_model.setSourceModel(self._library_model)
        self._sort_library_model.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._sort_library_model.setFilterKeyColumn(0)

    def setupFonts(self):
        """
        Setup fonts for the window
        """
        self._group_font = self.font()
        self._group_font.setBold(True)
        self._group_font.setPointSizeF(self.font().pointSize())
        self._group_font.setCapitalization(QtGui.QFont.AllUppercase)

        self._hint_font = self.font()
        self._hint_font.setBold(False)
        self._hint_font.setPointSizeF(self.font().pointSize() * 0.88)

    def setupWidgets(self):
        """
        Setup window widgets
        """
        self.setupMusic()
        self._vlayout.addSpacing(20)
        self.setupAdvanced()
        self.setLayout(self._vlayout)

    def setupMusic(self):
        """
        Setup widgets in 'Music' group
        """
        group_label = QtWidgets.QLabel("Music")
        group_label.setFont(self._group_font)
        self._vlayout.addWidget(group_label)

        hint = QtWidgets.QLabel("I want to listen to")
        self._vlayout.addWidget(hint)

        ctrl_layout = QtWidgets.QVBoxLayout()
        ctrl_layout.setSpacing(10)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)

        self.entire_library = QtWidgets.QRadioButton("The entire library", self)
        self.part_library = QtWidgets.QRadioButton("Portion of the library", self)

        self.music_library = QtWidgets.QButtonGroup(self)
        self.music_library.addButton(self.entire_library, self.MUSIC_LIBRARY_ENTIRE)
        self.music_library.addButton(self.part_library, self.MUSIC_LIBRARY_PORTION)
        self.music_library.buttonClicked.connect(self.onMusicLibraryClicked)

        ctrl_layout.addWidget(self.entire_library)
        ctrl_layout.addWidget(self.part_library)

        tree_layout = QtWidgets.QVBoxLayout()
        tree_layout.setContentsMargins(20, 0, 0, 0)
        tree_layout.setSpacing(4)

        self.search_library = QtWidgets.QLineEdit(self)
        self.search_library.setClearButtonEnabled(True)
        self.search_library.setPlaceholderText("Filter...")
        tree_layout.addWidget(self.search_library)

        self.library_tree = QtWidgets.QTreeView(self)
        self.library_tree.setHeaderHidden(True)
        self.library_tree.setModel(self._sort_library_model)
        self.library_tree.setSortingEnabled(True)
        self.library_tree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        tree_layout.addWidget(self.library_tree)

        ctrl_layout.addLayout(tree_layout)

        self._vlayout.addLayout(ctrl_layout)

        self.search_library.textChanged.connect(self.onSearchLibraryChanged)
        self._library_model.itemChanged.connect(self.onLibraryModelItemChanged)

    def setupAdvanced(self):
        """
        Setup widgets in 'Advanced' group
        """
        group_label = QtWidgets.QLabel("Advanced")
        group_label.setFont(self._group_font)
        self._vlayout.addWidget(group_label)

        ctrl_layout = QtWidgets.QVBoxLayout()
        ctrl_layout.setSpacing(2)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)

        hlayout = QtWidgets.QHBoxLayout()
        text = QtWidgets.QLabel("Show developer menu")
        self.show_developer = QtWidgets.QCheckBox()
        self.show_developer.clicked.connect(self.updateWidgets)
        hlayout.addWidget(text)
        hlayout.addStretch()
        hlayout.addWidget(self.show_developer)

        hint = QtWidgets.QLabel("Show tools for station development in menu")
        hint.setFont(self._hint_font)

        ctrl_layout.addLayout(hlayout)
        ctrl_layout.addWidget(hint)

        self._vlayout.addLayout(ctrl_layout)

    def updateWidgets(self):
        """
        Update widgets
        """
        part_library = self.part_library.isChecked()
        self.search_library.setEnabled(part_library)
        self.library_tree.setEnabled(part_library)

        self.preferencesUpdated.emit()

    def event(self, e):
        if e.type() == QtCore.QEvent.WindowActivate:
            self.window_action.setChecked(True)
        return super().event(e)

    def closeEvent(self, event):
        """
        Called when EventClose is recieved
        """
        self.window_action.setVisible(False)
        self.writeSettings()
        event.accept()

    def onMusicLibraryClicked(self, button):
        """
        Called when mucis library radio button was clicked
        """
        self.updateWidgets()

    def onLibraryModelItemChanged(self, item):
        """
        Called when item in the library tree was modified
        """
        if item.hasChildren():
            checkState = item.checkState()
            if checkState != QtCore.Qt.PartiallyChecked:
                for i in range(item.rowCount()):
                   item.child(i).setCheckState(checkState)
        else:
            diff = False
            parent = item.parent()
            for j in range(parent.rowCount()):
               if (j != item.row()) and (item.checkState() != parent.child(j).checkState()):
                   diff = True

            if diff:
                parent.setCheckState(QtCore.Qt.PartiallyChecked)
            else:
                parent.setCheckState(item.checkState())

            if item.checkState() == QtCore.Qt.Checked:
                self.user_selection[item.data()] = True
            else:
                del self.user_selection[item.data()]

    def onSearchLibraryChanged(self, text):
        """
        Called when library search filed is changed
        """
        if len(text) > 1:
            self._sort_library_model.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive))
        else:
            self._sort_library_model.setFilterRegExp("")

    def writeSettings(self):
        """
        Write settings
        """
        self._settings.beginGroup("PreferencesWindow")
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.endGroup()

        self._settings.beginGroup("Preferences/Music")
        self._settings.setValue("library_portion", self.music_library.checkedId())
        self._settings.setValue("user_selection", list(self.user_selection.keys()))
        self._settings.endGroup()

        self._settings.beginGroup("Preferences/Advanced")
        self._settings.setValue("show_develop_menu", self.show_developer.isChecked())
        self._settings.endGroup()

    def readSettings(self):
        """
        Read settings
        """
        self._settings.beginGroup("PreferencesWindow")
        geom = self._settings.value("geometry")
        if geom is None:
            pass
        else:
            self.restoreGeometry(geom)
        self._settings.endGroup()

        self._settings.beginGroup("Preferences/Music")
        portion = self._settings.value("library_portion", self.MUSIC_LIBRARY_ENTIRE)
        self.music_library.button(portion).setChecked(True)

        piece_ids = self._settings.value("user_selection", [])
        for pid in piece_ids:
            start = self._library_model.index(0, 0)
            idxs = self._library_model.match(start, QtCore.Qt.UserRole + 1, pid, 1, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
            if len(idxs) > 0:
                si = self._library_model.itemFromIndex(idxs[0])
                si.setCheckState(QtCore.Qt.Checked)
        self._settings.endGroup()

        self._settings.beginGroup("Preferences/Advanced")
        self.show_developer.setChecked(self._settings.value("show_develop_menu", False, type=bool))
        self._settings.endGroup()
