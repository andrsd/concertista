"""
AboutDialog.py
"""

from PyQt5 import QtCore, QtWidgets
from concertista import consts


class AboutDialog(QtWidgets.QDialog):
    """ About dialog """

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addSpacing(8)

        icon = QtWidgets.QApplication.windowIcon()
        self._icon = QtWidgets.QLabel()
        self._icon.setPixmap(icon.pixmap(64, 64))
        self._layout.addWidget(self._icon, 0, QtCore.Qt.AlignHCenter)

        self._title = QtWidgets.QLabel("Concertista")
        font = self._title.font()
        font.setBold(True)
        font.setPointSize(int(1.2 * font.pointSize()))
        self._title.setFont(font)
        self._title.setAlignment(QtCore.Qt.AlignHCenter)
        self._layout.addWidget(self._title)

        self._text = QtWidgets.QLabel(
            "Version {}\n"
            "\n"
            "Powered by spotify\n"
            "\n"
            "{}".format(consts.VERSION, consts.COPYRIGHT)
        )
        font = self._text.font()
        font.setPointSize(int(0.9 * font.pointSize()))
        self._text.setFont(font)
        self._text.setAlignment(QtCore.Qt.AlignHCenter)
        self._layout.addWidget(self._text)

        self.setLayout(self._layout)
        self.setWindowTitle("About")
