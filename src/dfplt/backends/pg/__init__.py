from dfplt.backends.pg.lineplot import Lineplot as pgLinePlot
import pyqtgraph as pg


from pandas.plotting._matplotlib.boxplot import (  # noqa:F401
    LinePlot,
    BoxPlot,
    boxplot,
    boxplot_frame,
    boxplot_frame_groupby,
)
from pandas.plotting._matplotlib.converter import (  # noqa:F401
    deregister,
    register,
)


from pandas.plotting._matplotlib.tools import table  # noqa:F401

from pandas.plotting._matplotlib.hist import (  # noqa:F401
    HistPlot,
    KdePlot,
    hist_frame,
    hist_series,
)

from pandas.plotting._matplotlib.misc import (  # noqa:F401
    andrews_curves,
    autocorrelation_plot,
    bootstrap_plot,
    lag_plot,
    parallel_coordinates,
    radviz,
    scatter_matrix,
)


class BarPlot(LinePlot):
    pass


class BarhPlot(LinePlot):
    pass


class AreaPlot(LinePlot):
    pass


class PiePlot(LinePlot):
    pass


class ScatterPlot(LinePlot):
    pass


class HexBinPlot(LinePlot):
    pass


PLOT_CLASSES = {"line": pgLinePlot}
PLOT_CLASSES_FALLBACK = {
    "line": LinePlot,
    "bar": BarPlot,
    "barh": BarhPlot,
    "box": BoxPlot,
    "hist": HistPlot,
    "kde": KdePlot,
    "area": AreaPlot,
    "pie": PiePlot,
    "scatter": ScatterPlot,
    "hexbin": HexBinPlot,
}


def plot(data, kind, **kwargs):
    fb = kwargs.pop("_fallbackBackend", False)
    if fb:
        kwargs.pop("x")
        kwargs.pop("y")
    if (kind in PLOT_CLASSES) and not fb:
        _ = pg.mkQApp()
        return PLOT_CLASSES[kind](data, **kwargs)
    else:
        plot_obj = PLOT_CLASSES_FALLBACK[kind](data, **kwargs)
        plot_obj.generate()
        plot_obj.draw()  # pragma: no cover
        return plot_obj.result  # pragma: no cover


# we add the entry point dynamically, so it also works in editable mode:
# https://stackoverflow.com/a/48666503
def _addEntryPoint():
    import pkg_resources

    d = pkg_resources.Distribution(__file__)
    ep = pkg_resources.EntryPoint.parse("dfplt = dfplt.backends:pg", dist=d)
    d._ep_map = {"pandas_plotting_backends": {"pg": ep}}
    pkg_resources.working_set.add(d, "pg")


_addEntryPoint()
