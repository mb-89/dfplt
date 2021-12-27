import functools
import pandas as pd

# we need this imports so that the backend gets registered
from dfplt.backends import pg  # noqa: F401


@functools.cache
def getAvailableBackends():
    beL = [
        "dfplt"
    ]  # , "matplotlib"] lets remove matplotlib until it properly supports pyside6
    df = pd.DataFrame()
    for (
        be
    ) in beL:  # we need to do this so all the backends are found in _core._backends
        try:
            df.plot(backend=be)
        except (IndexError, TypeError, ValueError):  # pragma: no cover
            continue
    return sorted(list(pd.plotting._core._backends))


getAvailableBackends()
pd.options.plotting.backend = "dfplt"
