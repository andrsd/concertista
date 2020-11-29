"""
PieceNameDialog.py
"""

import io
import yaml
import uuid
from PyQt5 import QtWidgets, QtCore, QtGui

class PieceNameDialog(QtWidgets.QDialog):
    """
    Piece name dialog
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

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

        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'YML (*.yml)')
        if file_name[0]:
            track_ids = []
            for track in self._tracks:
                track_ids.append(track['id'])

            obj = {
                "id": uuid.uuid4().hex,
                "composer_id": self._artist['id'],
                "name": self._piece_name_edit.text(),
                "album_id": self._album['id'],
                "tracks": track_ids
            }

            with io.open(file_name[0], 'w', encoding = 'utf8') as outfile:
                yaml.dump(obj, outfile, default_flow_style = False, allow_unicode = True)
