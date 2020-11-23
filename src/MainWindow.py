"""
MainWindow.py
"""

import os
import io
import yaml
from PyQt5 import QtWidgets, QtCore
import consts
from AboutDialog import AboutDialog

class MainWindow(QtWidgets.QMainWindow):
    """
    Main window
    """

    def __init__(self):
        super().__init__()
        # spotify object
        self._spotify = None
        # my spotify profile
        self._me = None
        self._settings = QtCore.QSettings()
        self._about_dlg = None

        self.readSettings()
        self.setupWidgets()
        self.setupMenuBar()
        self.updateMenuBar()

    def setupWidgets(self):
        """
        Setup widgets
        """
        w = QtWidgets.QWidget(self)
        w.setContentsMargins(0, 0, 0 ,0)
        layout = QtWidgets.QHBoxLayout()

        w.setLayout(layout)
        self.setCentralWidget(w)

    def setupMenuBar(self):
        """
        Setup menu bar
        """
        self.menubar = QtWidgets.QMenuBar(self)

        self.controls_menu = self.menubar.addMenu("Controls")
        self._play_pause = self.controls_menu.addAction("Play", self.onPlayPause, "Space")
        self._stop = self.controls_menu.addAction("Stop", self.onStop, "Ctrl+.")
        self._next = self.controls_menu.addAction("Next", self.onNext, "Ctrl+Right")
        self._previous = self.controls_menu.addAction("Previous", self.onPrevious, "Ctrl+Left")
        self.controls_menu.addSeparator()
        self._volume_up = self.controls_menu.addAction("Increase Volume", self.onVolumeUp, "Ctrl+Up")
        self._volume_down = self.controls_menu.addAction("Decrease Volume", self.onVolumeDown, "Ctrl+Down")
        self.controls_menu.addSeparator()

        # The "About" item is fine here, since we assume Mac and that will place the item into
        # different submenu but this will need to be fixed for linux and windows
        self.controls_menu.addSeparator()
        self._about_box_action = self.controls_menu.addAction("About", self.onAbout)

        self.window_menu = self.menubar.addMenu("Window")
        self._minimize = self.window_menu.addAction("Minimize", self.onMinimize, "Ctrl+M")
        self.window_menu.addSeparator()
        self._bring_all_to_front = self.window_menu.addAction("Bring All to Front",
            self.onBringAllToFront)

        self.window_menu.addSeparator()
        self._show_main_window = self.window_menu.addAction("Spotify Classical Radio", self.onShowMainWindow)
        self._show_main_window.setCheckable(True)

        self.action_group_windows = QtWidgets.QActionGroup(self)
        self.action_group_windows.addAction(self._show_main_window)

        self.setMenuBar(self.menubar)

    def updateMenuBar(self):
        """
        Update menu bar
        """
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self:
            self._show_main_window.setChecked(True)

    def onPlayPause(self):
        pass

    def onStop(self):
        pass

    def onNext(self):
        pass

    def onPrevious(self):
        pass

    def onVolumeUp(self):
        pass

    def onVolumeDown(self):
        pass

    def onAbout(self):
        """
        Called when FileAbout action is triggered
        """
        if self._about_dlg is None:
            self._about_dlg = AboutDialog(self)
        self._about_dlg.show()

    def onMinimize(self):
        """
        Called when WindowMinimize is triggered
        """
        self.showMinimized()

    def onBringAllToFront(self):
        """
        Called when WindowBringAllToFront is triggered
        """
        self.showNormal()

    def onShowMainWindow(self):
        """
        Called when show main window is triggered
        """
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.updateMenuBar()

    def event(self, event):
        """
        Event override
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        """
        Called when EventClose is recieved
        """
        self.writeSettings()
        event.accept()

    def writeSettings(self):
        """
        Write settings
        """
        self._settings.beginGroup("MainWindow")
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.endGroup()

        self._settings.beginGroup("spotify")
        self._settings.setValue("playlist_id", self._playlist_id)
        self._settings.endGroup()

    def readSettings(self):
        """
        Read settings
        """
        self._settings.beginGroup("MainWindow")
        geom = self._settings.value("geometry")
        if geom is None:
            screen_rc = QtWidgets.QApplication.desktop().screenGeometry()
            wnd_wd = 450
            wnd_ht = int(0.9 * screen_rc.height())
            self.setGeometry(QtCore.QRect(screen_rc.width() - wnd_wd - 10, (screen_rc.height() - wnd_ht) / 2, wnd_wd, wnd_ht))
        else:
            self.restoreGeometry(geom)
        self._settings.endGroup()

    def setupSpotify(self, spotify):
        self._spotify = spotify
        if spotify is None:
            return

        self._me = self._spotify.me()

        self._settings.beginGroup("spotify")
        self._playlist_id = self._settings.value("playlist_id")
        self._settings.endGroup()

        # Create our playlist if there is not one
        if self._playlist_id is None:
            pl = self._spotify.user_playlist_create(self._me['id'], "Classical Radio", public=False, description="Created by Spotify Classical Qt Application")
            self._playlist_id = pl['id']

        # TODO: check that playlist_id is valid
