import os
from pathlib import Path

from concertista import consts
from concertista.DB import DB

dir = Path(__file__).parent

def test_db_init(qtbot):
    db = DB()
    assert db._composers == {}
    assert db._pieces == {}
    assert db._pieces_by_composers == {}
    assert db._completer_model == None

def test_load_empty_db(qtbot):
    consts.MUSIC_DIR = os.path.join(dir, 'assets', 'music-empty')
    db = DB()
    db.load()
    assert db._composers == {}
    assert db._pieces == {}
    assert db._pieces_by_composers == {}
    assert db._completer_model != None

def test_load_simple_db(qtbot):
    consts.MUSIC_DIR = os.path.join(dir, 'assets', 'music')
    db = DB()
    db.load()

    assert 1234 in db._composers
    composer = db._composers[1234]
    assert composer['id'] == 1234
    assert composer['name'] == 'Composer 1'
    pieces = db._pieces
    assert 'id001' in pieces
    p001 = pieces['id001']
    assert p001['album_id'] == 'a987'
    assert p001['composer_id'] == 1234
    assert p001['id'] == 'id001'
    assert p001['name'] == 'Piece 1'
    assert 'tracks' in p001
    tracks = p001['tracks']
    assert tracks[0] == 123
    assert tracks[1] == 456
    assert tracks[2] == 789
