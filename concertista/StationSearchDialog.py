"""
StationSearchDialog.py
"""

from PyQt5 import QtWidgets, QtCore


class StationSearchDialog(QtWidgets.QDialog):
    """
    Station by composer
    """

    def __init__(self, db, parent):
        super().__init__(parent)
        self._db = db
        self.db_item = None
        self._parent = parent
        self.setMinimumWidth(500)

        self._layout = QtWidgets.QVBoxLayout()

        self.search = QtWidgets.QLineEdit(self)
        self.search.setPlaceholderText("What are you looking for?")
        self.search.setClearButtonEnabled(True)
        self._completer = QtWidgets.QCompleter(
            self._db.get_completer_model(), self.search)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setFilterMode(QtCore.Qt.MatchContains)
        self.search.setCompleter(self._completer)
        self.search.textChanged.connect(self.onSearchTextChanged)
        self._layout.addWidget(self.search)

        # --- buttons ---
        self._button_layout = QtWidgets.QHBoxLayout()

        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._cancel_button.clicked.connect(self.reject)
        self._button_layout.addWidget(self._cancel_button)

        self._button_layout.addStretch()

        self._play_button = QtWidgets.QPushButton("Play")
        self._play_button.setDefault(True)
        self._play_button.setEnabled(False)
        self._play_button.clicked.connect(self.onPlay)
        self._button_layout.addWidget(self._play_button)
        self._layout.addLayout(self._button_layout)

        self.setLayout(self._layout)
        self.setWindowTitle("Search")

    def updateWidgets(self):
        """
        Update widgets on UI change
        """
        items = self._completer.model().findItems(self.search.text())
        if len(items) == 1:
            self._play_button.setEnabled(True)
            self.db_item = items[0].data()
        else:
            self._play_button.setEnabled(False)
            self.db_item = None

    def onSearchTextChanged(self, text):
        """
        Called when search text has changed
        """
        self.updateWidgets()

    def onPlay(self):
        """
        Called when clicked on 'Play' button
        """
        self.accept()
