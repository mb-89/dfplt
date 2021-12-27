import pytest
import pytestqt  # noqa:F401 we need this so its added to the requirements.txt

from pyqtgraph.Qt import mkQApp


@pytest.fixture(scope="session")
def qapp():
    yield mkQApp()
