from PyQt5 import QtGui

from concertista.assets import Assets


def test_singleton():
    assert Assets() is Assets()
    assert Assets().author_icon is Assets().author_icon
    assert Assets().piece_icon is Assets().piece_icon
    assert Assets().prev_icon is Assets().prev_icon
    assert Assets().next_icon is Assets().next_icon
    assert Assets().play_icon is Assets().play_icon
    assert Assets().pause_icon is Assets().pause_icon


def test_has_logo():
    assert isinstance(Assets().author_icon, QtGui.QIcon)
    assert isinstance(Assets().piece_icon, QtGui.QIcon)
    assert isinstance(Assets().prev_icon, QtGui.QIcon)
    assert isinstance(Assets().next_icon, QtGui.QIcon)
    assert isinstance(Assets().play_icon, QtGui.QIcon)
    assert isinstance(Assets().pause_icon, QtGui.QIcon)
