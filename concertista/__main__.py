"""
Concertista
"""

import sys
import os
import signal
from concertista import consts
from concertista import server

from PyQt5 import QtWidgets, QtGui, QtCore
from concertista.MainWindow import MainWindow


def safe_timer(timeout, func, *args, **kwargs):
    """Create a timer that is safe against garbage collection and
    overlapping calls.
    See: http://ralsina.me/weblog/posts/BB974.html
    """
    def timer_event():
        try:
            func(*args, **kwargs)
        finally:
            QtCore.QTimer.singleShot(timeout, timer_event)
    QtCore.QTimer.singleShot(timeout, timer_event)


def handle_sigint(signum, frame):
    QtWidgets.QApplication.quit()


def handle_uncaught_exception(exc_type, exc, traceback):
    print('Unhandled exception', exc_type, exc, traceback)
    QtWidgets.QApplication.quit()


sys.excepthook = handle_uncaught_exception


def main():
    QtCore.QCoreApplication.setOrganizationName("David Andrs")
    QtCore.QCoreApplication.setOrganizationDomain("name.andrs")
    QtCore.QCoreApplication.setApplicationName(consts.APP_NAME)

    qapp = QtWidgets.QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)

    server_thread = server.ServerThread()
    server_thread.start()

    window = MainWindow()
    signal.signal(signal.SIGINT, handle_sigint)
    window.connectToSpotify()
    window.show()

    # Repeatedly run python-noop to give the interpreter time to
    # handle signals
    safe_timer(50, lambda: None)

    qapp.exec()

    del window
    del qapp


if __name__ == '__main__':
    main()
