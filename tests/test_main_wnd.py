from unittest.mock import MagicMock, patch
from PyQt5 import QtCore
from concertista.PreferencesWindow import PreferencesWindow


@patch('concertista.DB.DB.get_pieces')
def test_randomize_pieces(pcs_mock, main_window):
    pcs_mock.return_value = {
        'a': {'tracks': ['1', '2']},
        'b': {'tracks': ['3', '4']}
    }

    piece_ids = ['b']
    uris = main_window.randomizePieces(piece_ids)
    assert uris[0] == 'spotify:track:3'
    assert uris[1] == 'spotify:track:4'


def test_on_new_station_all_lib(main_window):
    spotify = MagicMock()
    main_window._active_device_id = 1
    main_window._spotify = spotify
    main_window.onNewStation()

    spotify.start_playback.assert_called_once()


@patch('concertista.MainWindow.MainWindow.randomizePieces')
def test_on_new_station_subset_lib(rnd_pcs_mock, main_window):
    rnd_pcs_mock.return_value = ['a:b:c']

    spotify = MagicMock()
    main_window._active_device_id = 1
    main_window._spotify = spotify
    main_window._preferences_window = MagicMock()
    main_window._preferences_window.user_selection = {'a': '1'}
    main_window._preferences_window.music_library.checkedId.return_value = \
        PreferencesWindow.MUSIC_LIBRARY_PORTION
    main_window.onNewStation()

    spotify.start_playback.assert_called_once()


@patch('concertista.MainWindow.MainWindow.reportUnknownDeviceId')
def test_on_new_station_unk_dev(report_mock, main_window):
    main_window._active_device_id = None
    main_window.onNewStation()

    assert report_mock.call_count == 1


def test_on_network_reply_localhost(main_window):
    reply = MagicMock()
    reply.url().host.return_value = 'localhost'
    main_window.onNetworkReply(reply)


@patch('spotipy.Spotify.current_playback')
def test_update_currently_playing_play(cpb, main_window):
    spotify = MagicMock()
    spotify.current_playback.return_value = {
        'is_playing': True
    }
    main_window._spotify = spotify
    main_window.updateCurrentlyPlaying()


@patch('spotipy.Spotify.current_playback')
def test_update_currently_playing_pause(cpb, main_window):
    spotify = MagicMock()
    spotify.current_playback.return_value = {
        'is_playing': False,
        'item': {
            'name': 'item',
            'artists': [
                {'name': 'artist1'},
                {'name': 'artist2'}
            ],
            'album': {
                'images': [
                    {'height': 300, 'url': 'URL'}
                ]
            }
        }
    }
    main_window._spotify = spotify
    main_window._nam = MagicMock()
    main_window.updateCurrentlyPlaying()

    main_window._nam.get.assert_called_once()


@patch('PyQt5.QtWidgets.QLabel.setPixmap')
@patch('PyQt5.QtGui.QImage')
@patch('PyQt5.QtGui.QPixmap.fromImage')
def test_on_network_reply(pix, qimg, set_pix, main_window):
    reply = MagicMock()
    reply.url().host.return_value = '1.2.3.4'
    main_window.onNetworkReply(reply)

    pix.assert_called_once()
    qimg.assert_called_once()
    set_pix.assert_called_once()


@patch('PyQt5.QtWidgets.QMessageBox.exec')
def test_report_unknown_dev_id(exec, main_window):
    main_window.reportUnknownDeviceId()
    exec.assert_called_once()


def test_on_station_search(main_window):
    main_window._station_search_dlg = MagicMock()
    main_window.onStationSearch()
    main_window._station_search_dlg.open.assert_called_once()


@patch('concertista.MainWindow.MainWindow.randomizePieces')
def test_on_station_search_play_piece(rnd_pcs, main_window):
    spotify = MagicMock()
    main_window._spotify = spotify

    rnd_pcs.return_value = ['a:b:c']

    main_window._active_device_id = 1
    main_window._station_search_dlg = MagicMock()
    main_window._station_search_dlg.db_item = {
        'type': 'piece',
        'id': 1234
    }
    main_window.onStationSearchPlay()

    spotify.start_playback.assert_called_once_with(device_id=1, uris=['a:b:c'])


@patch('concertista.MainWindow.MainWindow.randomizePieces')
def test_on_station_search_play_composer(rnd_pcs, main_window):
    spotify = MagicMock()
    main_window._spotify = spotify

    rnd_pcs.return_value = ['a:b:c']

    main_window._active_device_id = 1
    main_window._station_search_dlg = MagicMock()
    main_window._station_search_dlg.db_item = {
        'type': 'composer',
        'id': 1234
    }
    main_window.onStationSearchPlay()

    spotify.start_playback.assert_called_once_with(device_id=1, uris=['a:b:c'])


@patch('concertista.MainWindow.MainWindow.reportUnknownDeviceId')
def test_on_station_search_play_unk_dev(report_mock, main_window):
    main_window._active_device_id = None
    main_window.onStationSearchPlay()

    assert report_mock.call_count == 1


@patch('concertista.DeveloperWindow.DeveloperWindow.show')
@patch('concertista.DeveloperWindow.DeveloperWindow.setupSpotify')
@patch('concertista.DeveloperWindow.DeveloperWindow.readSettings')
def test_on_developer(read_set, setup, show, main_window):
    main_window.onDeveloper()
    setup.assert_called_once()
    show.assert_called_once()


def test_on_pause(main_window):
    spotify = MagicMock()
    spotify.current_playback.return_value = {
        'is_playing': True,
    }
    main_window._spotify = spotify
    main_window.onPlayPause()
    spotify.pause_playback.assert_called_once()


def test_on_play(main_window):
    spotify = MagicMock()
    spotify.current_playback.return_value = {
        'is_playing': False,
    }
    main_window._spotify = spotify
    main_window.onPlayPause()
    spotify.start_playback.assert_called_once()


@patch('PyQt5.QtCore.QTimer.singleShot')
def test_on_next(tmr, main_window):
    spotify = MagicMock()
    main_window._spotify = spotify
    main_window.onNext()
    spotify.next_track.assert_called_once()
    tmr.assert_called_once()


@patch('PyQt5.QtCore.QTimer.singleShot')
def test_on_previous(tmr, main_window):
    spotify = MagicMock()
    main_window._spotify = spotify
    main_window.onPrevious()
    spotify.previous_track.assert_called_once()
    tmr.assert_called_once()


def test_on_volume_up(main_window):
    spotify = MagicMock()
    main_window._volume = 0
    main_window._volume_slider = spotify
    main_window.onVolumeUp()
    main_window._volume_slider.setValue.assert_called_once()


def test_on_volume_down(main_window):
    spotify = MagicMock()
    main_window._volume = 0
    main_window._volume_slider = spotify
    main_window.onVolumeDown()
    main_window._volume_slider.setValue.assert_called_once()


def test_on_volume_changed(main_window):
    spotify = MagicMock()
    main_window._spotify = spotify
    main_window.onVolumeChanged(2)
    spotify.volume.assert_called_once()
    assert main_window._volume == 2


@patch('concertista.AboutDialog.AboutDialog.show')
def test_on_about(show, main_window):
    main_window.onAbout()
    show.assert_called_once()


def test_on_current_device_changed(main_window):
    spotify = MagicMock()
    main_window._active_device_id = 1
    main_window._spotify = spotify

    main_window.onCurrentDeviceChanged(1)

    spotify.transfer_playback.assert_called_once()


@patch('concertista.MainWindow.MainWindow.showMinimized')
def test_on_minimize(show, main_window):
    main_window.onMinimize()
    show.assert_called_once()


@patch('concertista.MainWindow.MainWindow.showNormal')
def test_on_bring_all_to_front(show, main_window):
    main_window.onBringAllToFront()
    show.assert_called_once()


@patch('concertista.MainWindow.MainWindow.showNormal')
def test_on_show_main_window(show, main_window):
    main_window.onShowMainWindow()
    show.assert_called_once()


@patch('concertista.PreferencesWindow.PreferencesWindow.showNormal')
@patch('concertista.PreferencesWindow.PreferencesWindow.raise_')
def test_on_show_preferences(rise, show, main_window):
    main_window.onShowPreferences()
    show.assert_called_once()
    rise.assert_called_once()


@patch('concertista.PreferencesWindow.PreferencesWindow.show')
def test_on_preferences(show, main_window):
    main_window.onPreferences()
    show.assert_called_once()


@patch('concertista.MainWindow.MainWindow.updateMenuBar')
def test_on_preferences_updated(update_menu, main_window):
    main_window.onPreferencesUpdated()
    update_menu.assert_called_once()


@patch('PyQt5.QtWidgets.QMainWindow.event')
@patch('concertista.MainWindow.MainWindow.updateMenuBar')
def test_activate_window_event(update_menu, event, main_window):
    e = MagicMock()
    e.type.return_value = QtCore.QEvent.WindowActivate
    main_window.event(e)
    update_menu.assert_called_once()


@patch('concertista.MainWindow.MainWindow.updateCurrentlyPlayingTitle')
def test_resize_event(update, main_window):
    e = MagicMock()
    main_window.resizeEvent(e)
    update.assert_called_once()


@patch('concertista.MainWindow.MainWindow.restoreGeometry')
@patch('concertista.MainWindow.MainWindow.setGeometry')
def test_read_settings_initial(set_geometry, restore_mock, main_window):
    def val(arg, default=None, **kwargs):
        if arg == 'geometry':
            return None

    main_window._settings = MagicMock()
    main_window._settings.value = val

    main_window.readSettings()

    restore_mock.assert_not_called()
    set_geometry.assert_called_once()


def test_connect_to_spotify(main_window):
    nam = MagicMock()
    main_window._nam = nam
    main_window.connectToSpotify()
    nam.get.assert_called_once()


def test_setup_spotify(main_window):
    spotify = MagicMock()
    spotify.devices.return_value = {
        'devices': [
            {'id': 1, 'volume_percent': 10, 'is_active': True, 'name': 'a'},
            {'id': 2, 'volume_percent': 5, 'is_active': False, 'name': 'b'},
        ]
    }
    main_window.setupSpotify(spotify)
