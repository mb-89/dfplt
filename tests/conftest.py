import pytest
import pytestqt  # noqa:F401 we need this so its added to the requirements.txt

from pyqtgraph import Qt
import os


def pytest_configure(config):
    # force qtbot to use the same backend as pyqtgraph
    os.environ["PYTEST_QT_API"] = Qt.QT_LIB.lower()


@pytest.fixture(scope="session")
def qapp():
    yield Qt.mkQApp()
