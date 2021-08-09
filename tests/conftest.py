import pytest

from unittest.mock import MagicMock, patch

def pytest_configure(config):
    # Ignore logging configuration for BeeRef during test runs. This
    # avoids logging to the regular log file and spamming test output
    # with debug messages.
    #
    # This needs to be done before the application code is even loaded since
    # logging configuration happens on module level
    import logging.config
    logging.config.dictConfig = MagicMock


@pytest.fixture
def main_window(qtbot):
    from concertista.MainWindow import MainWindow
    main = MainWindow()
    qtbot.addWidget(main)
    yield main
