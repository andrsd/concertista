"""
PreferencesWindow.py
"""

from PyQt5 import QtWidgets, QtCore, QtGui

class PreferencesWindow(QtWidgets.QDialog):
    """
    Preferences
    """
    preferencesUpdated = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.window_action = None
        self.setMinimumWidth(500)
        self.setWindowTitle("Preferences")
        self.setWindowFlags((self.windowFlags() | QtCore.Qt.CustomizeWindowHint) & ~QtCore.Qt.WindowMaximizeButtonHint)
        self._settings = QtCore.QSettings()
        self._vlayout = QtWidgets.QVBoxLayout()

        self.setupFonts()
        self.setupWidgets()
        self.readSettings()

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
        self.music_library.addButton(self.entire_library, 0)
        self.music_library.addButton(self.part_library, 1)
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
        tree_layout.addWidget(self.library_tree)

        ctrl_layout.addLayout(tree_layout)

        self._vlayout.addLayout(ctrl_layout)

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

    def writeSettings(self):
        """
        Write settings
        """
        self._settings.beginGroup("PreferencesWindow")
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.endGroup()

        self._settings.beginGroup("Preferences/Music")
        self._settings.setValue("library_portion", self.music_library.checkedId())
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
        self.music_library.button(self._settings.value("library_portion", 0)).setChecked(True)
        self._settings.endGroup()

        self._settings.beginGroup("Preferences/Advanced")
        self.show_developer.setChecked(self._settings.value("show_develop_menu", False))
        self._settings.endGroup()
