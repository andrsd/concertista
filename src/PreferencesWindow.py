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
        self.setupAdvanced()
        self._vlayout.addStretch()
        self.setLayout(self._vlayout)

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

    def writeSettings(self):
        """
        Write settings
        """
        self._settings.beginGroup("PreferencesWindow")
        self._settings.setValue("geometry", self.saveGeometry())
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

        self._settings.beginGroup("Preferences/Advanced")
        self.show_developer.setChecked(self._settings.value("show_develop_menu", False))
        self._settings.endGroup()
