import pytest


@pytest.fixture
def main_window(qtbot):
    from concertista.MainWindow import MainWindow
    main = MainWindow()
    qtbot.addWidget(main)
    yield main
