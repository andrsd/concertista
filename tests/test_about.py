from PyQt5 import QtWidgets
from concertista.AboutDialog import AboutDialog


def test_about_dialog(main_window):
    about_dlg = AboutDialog(main_window)

    assert isinstance(about_dlg, AboutDialog)
    assert about_dlg.windowTitle() == 'About'
    assert isinstance(about_dlg._layout, QtWidgets.QVBoxLayout)
