"""
Classical radio using spotify
"""
# pylint: disable=invalid-name

import sys
import os
import argparse
import signal
import importlib.util
import consts

# pylint: disable=invalid-name
otter_dir = None

def check_requirements():
    """
    Check that all packages we are using are present. If not, let users know.
    """
    stop = False

    # check system packages
    modules = [ 'PyQt5', 'yaml', 'spotipy']
    not_found_modules = []
    for m in modules:
        if importlib.util.find_spec(m) is None:
            not_found_modules.append(m)

    if len(not_found_modules) > 0:
        print("The following modules were not found: {}. "
            "This may be fixed by installing them either "
            "via 'pip' or 'conda'.".format(", ".join(not_found_modules)))
        stop = True

    if len(not_found_modules) > 0:
        print("The following modules were not found: {}. "
            "This may be fixed by setting MOOSE_DIR environment "
            "variable.".format(", ".join(not_found_modules)))
        stop = True

    if stop:
        sys.exit(1)


def run():
    """
    Run the application
    """
    check_requirements()

    # pylint: disable=import-outside-toplevel
    import yaml
    import spotipy
    import spotipy.util
    from PyQt5 import QtWidgets, QtGui, QtCore
    from MainWindow import MainWindow
    from DB import DB

    QtCore.QCoreApplication.setOrganizationName("David Andrs")
    QtCore.QCoreApplication.setOrganizationDomain("name.andrs")
    QtCore.QCoreApplication.setApplicationName("SpotifyClassicalQt")

    qapp = QtWidgets.QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)

    # ---
    with open('.config.yml', 'rt') as f:
        config = yaml.safe_load(f)

    token = spotipy.util.prompt_for_user_token(
            username = config['username'],
            scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-modify-private',
            client_id = config['client-id'],
            client_secret = config['client-secret'],
            redirect_uri = config['redirect-uri'])

    spotify = spotipy.Spotify(auth = token)
    spotify.trace = False
    # ---

    # read the db
    db = DB("spotify")
    db.load()

    window = MainWindow()
    window.setupDB(db)
    window.setupSpotify(spotify)
    window.show()

    sys.exit(qapp.exec_())

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    run()
