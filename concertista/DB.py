"""
DB.py
"""
import os
import yaml
import consts
from PyQt5 import QtCore, QtGui

class DB:
    """
    Database with the music
    """

    def __init__(self):
        self._composers = {}
        self._pieces = {}
        # composer_id -> dict(piece ids)
        self._pieces_by_composers = {}
        self._completer_model = None

    def load(self):
        """
        Read database from location
        """
        self._load_composers()
        self._load_pieces()
        self._build_completer_model()

    def get_pieces(self):
        return self._pieces

    def get_composers(self):
        return self._composers

    def get_composer_pieces(self, composer_id):
        return self._pieces_by_composers[composer_id]

    def get_completer_model(self):
        return self._completer_model

    def _load_composers(self):
        composers = []
        with open(consts.MUSIC_DIR + '/composers.yml', 'rt', encoding = "utf-8") as f:
            composers = yaml.safe_load(f)

        for c in composers:
            id = c['id']
            self._composers[id] = c;

    def _load_pieces(self):
        for root, dirs, files in os.walk(consts.MUSIC_DIR + "/tracks"):
            path = root.split(os.sep)
            for file in files:
                if file.endswith(('.yml')):
                    try:
                        with open(root + '/' + file, 'rt', encoding = "utf-8") as f:
                            piece = yaml.safe_load(f)

                        piece_id = piece['id']
                        self._pieces[piece_id] = piece

                        composer_id = piece['composer_id']
                        if composer_id not in self._pieces_by_composers:
                            self._pieces_by_composers[composer_id] = []
                        self._pieces_by_composers[composer_id].append(piece_id)
                    except:
                        print("Error loading file:", file)

    def _build_completer_model(self):
        self._author_icon = QtGui.QIcon(os.path.join(consts.ICONS_DIR, "author.svg"))
        self._piece_icon = QtGui.QIcon(os.path.join(consts.ICONS_DIR, "vinyl.svg"))

        self._completer_model = QtGui.QStandardItemModel()

        for id, composer in self._composers.items():
            si = QtGui.QStandardItem(self._author_icon, "{}".format(composer['name']))
            si.setData({"type": "composer", "id": id})
            self._completer_model.appendRow(si)
            self._completer_model.setData(si.index(), QtCore.QSize(20, 20), QtCore.Qt.SizeHintRole)

        for id, piece in self._pieces.items():
            si = QtGui.QStandardItem(self._piece_icon, "{}: {}".format(piece['name'], self._composers[piece['composer_id']]['name']))
            si.setData({"type": "piece", "id": id})
            self._completer_model.appendRow(si)
            self._completer_model.setData(si.index(), QtCore.QSize(20, 20), QtCore.Qt.SizeHintRole)
