"""
DB.py
"""
import os
import yaml
import uuid

class DB:
    """
    Database with the music
    """

    def __init__(self, dir):
        self._dir = dir
        self._composers = []
        self._pieces = {}
        self._pieces_by_composers = {}

    def load(self):
        """
        Read database from location
        """
        self._load_composers()
        self._load_pieces()

    def get_pieces(self):
        return self._pieces

    def _load_composers(self):
        with open(self._dir + '/composers.yml', 'rt') as f:
            self._composers = yaml.safe_load(f)

    def _load_pieces(self):
        for root, dirs, files in os.walk(self._dir + "/tracks"):
            path = root.split(os.sep)
            for file in files:
                with open(root + '/' + file, 'rt') as f:
                    piece = yaml.safe_load(f)

                id = uuid.uuid4()
                peice_id = id.hex;
                self._pieces[peice_id] = piece

                composer_id = piece['composer_id']
                if composer_id not in self._pieces_by_composers:
                    self._pieces_by_composers[composer_id] = []
                self._pieces_by_composers[composer_id].append(piece)
