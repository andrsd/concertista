"""
StationByComposerDialog.py
"""

import io
import yaml
from PyQt5 import QtWidgets, QtCore, QtGui

class StationByComposerDialog(QtWidgets.QDialog):
    """
    Station by composer
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self._layout = QtWidgets.QVBoxLayout()

        self._composer_name = QtWidgets.QComboBox(self)
        self._layout.addWidget(self._composer_name)

        # --- buttons ---
        self._button_layout = QtWidgets.QHBoxLayout()

        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._cancel_button.clicked.connect(self.reject)
        self._button_layout.addWidget(self._cancel_button)

        self._button_layout.addStretch()

        self._play_button = QtWidgets.QPushButton("Play")
        self._play_button.setDefault(True)
        self._play_button.clicked.connect(self.onPlay)
        self._button_layout.addWidget(self._play_button)
        self._layout.addLayout(self._button_layout)

        self.setLayout(self._layout)

    def setupDB(self, db):
        """
        Setup DB
        """
        self._composers = db.get_composers()
        for c in self._composers:
            self._composer_name.addItem(c['name'], c)

    def onPlay(self):
        """
        Called when clicked on 'Play' button
        """
        self._artist = self._composer_name.currentData()
        self.accept()
