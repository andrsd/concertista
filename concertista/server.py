import os
import uuid
import webbrowser

from flask import Flask, request, redirect
from waitress import serve

import spotipy
import spotipy.util
from spotipy.oauth2 import SpotifyOAuth
if 'CI_TEST' in os.environ:
    SPOTIFY_CLIENT_ID = 'ID'
    SPOTIFY_CLIENT_SECRET = 's3cr3t'
    SPOTIFY_REDIRECT_URI = 'http://localhost:9182'
else: # pragma: no cover
    from concertista.spotify_creds import *

from PyQt5 import QtCore
from pathlib import Path

# port where we run  our http server so we can talk to spotify
port = int(os.environ.get("CONCERTISTA_PORT", 9182))

app = Flask(__name__)

caches_folder = str(Path.home()) + '/.cache/concertista/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + 'spotify'

@app.route('/')
def index():
    scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=scope,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        cache_path=session_cache_path(),
        show_dialog=True)

    if request.args.get("code"):
        # Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.get_cached_token():
        # Send user to spotify authorization page
        auth_url = auth_manager.get_authorize_url()
        webbrowser.open_new(auth_url)
        return f'Redirected to <a href="{auth_url}">Spotify authorization page</a>.'

    # Signed in, display info
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    signaler.connectToSpotify.emit(spotify)
    return f'<center>'\
           f'<h1>Concertista</h1>' \
           f'{spotify.me()["display_name"]}, access to your account was granted. <br/>' \
           f'You can close this window, now.' \
           f'</center>'


class ServerThread(QtCore.QThread):
    """
    Server thread for spotify authorization
    """

    def run(self):
        """
        Thread body
        """
        serve(app, host="0.0.0.0", port=port)


class Signaler(QtCore.QObject):
    """
    Singaler class to communicate with Qt
    """

    connectToSpotify = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        pass

signaler = Signaler()
