"""
Concertista
"""

import sys
import os
import signal
import consts
import server

from PyQt5 import QtWidgets, QtGui, QtCore
from MainWindow import MainWindow

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setOrganizationName("David Andrs")
    QtCore.QCoreApplication.setOrganizationDomain("name.andrs")
    QtCore.QCoreApplication.setApplicationName("Concertista")

    qapp = QtWidgets.QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)

    server_thread = server.ServerThread()
    server_thread.start()

    window = MainWindow()
    window.connectToSpotify()
    window.show()

    sys.exit(qapp.exec_())
