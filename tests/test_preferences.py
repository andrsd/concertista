from PyQt5 import QtCore
from unittest.mock import MagicMock, patch
from concertista.PreferencesWindow import PreferencesWindow


def test_init(pref_dlg):
    assert isinstance(pref_dlg, PreferencesWindow)


@patch('PyQt5.QtWidgets.QDialog.event')
def test_activate_window_event(event_mock, pref_dlg):
    pref_dlg.window_action = MagicMock()

    e = MagicMock()
    e.type.return_value = QtCore.QEvent.WindowActivate

    pref_dlg.event(e)

    pref_dlg.window_action.setChecked.assert_called_once_with(True)
    event_mock.assert_called_once_with(e)


@patch('concertista.PreferencesWindow.PreferencesWindow.writeSettings')
def test_close_event(write_mock, pref_dlg):
    pref_dlg.window_action = MagicMock()

    e = MagicMock()

    pref_dlg.closeEvent(e)

    write_mock.assert_called_once()
    e.accept.assert_called_once()


def test_write_settings(pref_dlg):
    pref_dlg._settings = MagicMock()

    pref_dlg.writeSettings()

    assert pref_dlg._settings.beginGroup.call_count == 3
    assert pref_dlg._settings.endGroup.call_count == 3


@patch('concertista.PreferencesWindow.PreferencesWindow.restoreGeometry')
def test_read_settings(restore_mock, pref_dlg):
    pref_dlg._settings = MagicMock()

    pref_dlg.readSettings()


@patch('concertista.PreferencesWindow.PreferencesWindow.restoreGeometry')
def test_read_settings_initial(restore_mock, pref_dlg):
    def val(arg, default=None, **kwargs):
        if arg == 'geometry':
            return None
        elif arg == 'library_portion':
            return 0
        elif arg == 'user_selection':
            return []
        elif arg == 'show_develop_menu':
            return False

    pref_dlg._settings = MagicMock()
    pref_dlg._settings.value = val

    pref_dlg.readSettings()

    restore_mock.assert_not_called()


def test_read_settings_partial_lib(pref_dlg):
    def val(arg, default=None, **kwargs):
        if arg == 'geometry':
            return None
        elif arg == 'library_portion':
            return 0
        elif arg == 'user_selection':
            return [0, 1]
        elif arg == 'show_develop_menu':
            return False

    pref_dlg._library_model = MagicMock()
    pref_dlg._library_model.match.return_value = [1]
    si = MagicMock()
    pref_dlg._library_model.itemFromIndex.return_value = si

    pref_dlg._settings = MagicMock()
    pref_dlg._settings.value = val

    pref_dlg.readSettings()

    assert si.setCheckState.call_count == 2


def test_search_lib_changed(pref_dlg):
    model = MagicMock()
    pref_dlg._sort_library_model = model

    pref_dlg.onSearchLibraryChanged('')

    model.setFilterRegExp.assert_called_once_with("")


def test_search_lib_changed_with_text(pref_dlg):
    model = MagicMock()
    pref_dlg._sort_library_model = model

    pref_dlg.onSearchLibraryChanged('asdf')

    model.setFilterRegExp.assert_called_once_with(
        QtCore.QRegExp('asdf', QtCore.Qt.CaseInsensitive))


@patch('concertista.PreferencesWindow.PreferencesWindow.updateWidgets')
def test_music_library_clicked(update_mock, pref_dlg):
    btn = MagicMock()
    pref_dlg.onMusicLibraryClicked(btn)
    update_mock.assert_called_once()


def test_libray_model_item_changed_children(pref_dlg):
    item = MagicMock()
    item.hasChildren.return_value = True
    item.checkState.return_value = QtCore.Qt.Checked
    item.rowCount.return_value = 2
    item.child.return_value = MagicMock()
    pref_dlg.onLibraryModelItemChanged(item)

    assert item.child.call_count == 2


def test_libray_model_item_changed_root(pref_dlg):
    pref_dlg.user_selection = {'1': False}

    parent = MagicMock()
    parent.rowCount.return_value = 1

    item = MagicMock()
    item.hasChildren.return_value = False
    item.parent.return_value = parent
    item.row.return_value = 0
    item.checkState.return_value = QtCore.Qt.Unchecked
    item.data.return_value = '1'
    parent.child.checkState.return_value = QtCore.Qt.Unchecked

    pref_dlg.onLibraryModelItemChanged(item)

    assert len(pref_dlg.user_selection.keys()) == 0


def test_libray_model_item_changed_root2(pref_dlg):
    pref_dlg.user_selection = {'1': False}

    parent = MagicMock()
    parent.rowCount.return_value = 1

    item = MagicMock()
    item.hasChildren.return_value = False
    item.parent.return_value = parent
    item.row.return_value = 1
    item.checkState.return_value = QtCore.Qt.Checked
    item.data.return_value = '1'
    parent.child.checkState.return_value = QtCore.Qt.Unchecked

    pref_dlg.onLibraryModelItemChanged(item)

    assert pref_dlg.user_selection['1'] is True
