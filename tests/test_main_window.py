from unittest.mock import patch


@patch('concertista.AboutDialog.AboutDialog.show')
def test_about_dialog(show_mock, main_window):
    main_window.onAbout()
    # show_mock.assert_called_once()
