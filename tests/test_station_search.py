from unittest.mock import MagicMock, patch
from concertista.StationSearchDialog import StationSearchDialog


def test_station_search_dlg(main_window):
    db = MagicMock()
    dlg = StationSearchDialog(db, main_window)

    assert isinstance(dlg, StationSearchDialog)


def test_search_non_existent(main_window):
    """
    Search for non-existent item
    """
    db = MagicMock()

    completer = MagicMock()
    completer.model().findItems.return_value = []

    dlg = StationSearchDialog(db, main_window)
    dlg._completer = completer

    dlg.onSearchTextChanged('asdf')

    assert dlg._play_button.isEnabled() is False
    assert dlg.db_item is None


def test_search_for_existing(main_window):
    """
    Search for existening item
    """
    db = MagicMock()
    dlg = StationSearchDialog(db, main_window)

    item = MagicMock()
    item.data.return_value = 'qwer'

    completer = MagicMock()
    completer.model().findItems.return_value = [item]
    dlg._completer = completer

    dlg.onSearchTextChanged('asdf')

    assert dlg._play_button.isEnabled() is True
    assert dlg.db_item == 'qwer'


@patch('concertista.StationSearchDialog.StationSearchDialog.accept')
def test_play(accept_mock, main_window):
    db = MagicMock()
    dlg = StationSearchDialog(db, main_window)
    dlg.onPlay()

    accept_mock.assert_called_once()
