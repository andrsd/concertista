# pylint: disable=invalid-name
"""
Constants
"""
import sys
import os
from pathlib import Path

APP_NAME = "Concertista"
VERSION = 1.0
COPYRIGHT = u"Copyright © 2020, David Andrš, All Rights Reserved"

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    CONCERTISTA_DIR = Path(sys._MEIPASS)
else:
    CONCERTISTA_DIR = Path(__file__).parent
MUSIC_DIR = os.path.join(CONCERTISTA_DIR, 'assets', 'music')
ICONS_DIR = os.path.join(CONCERTISTA_DIR, 'assets', 'icons')
