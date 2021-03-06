from dfplt.backends.pg.lineplot import Lineplot as pgLinePlot
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

# remove fallbacks until matplotlib properly supports pyside6
# import matplotlib
# import matplotlib.pyplot as plt
# plt.ioff()
# matplotlib.use("Qt5Agg")

# remove fallbacks until matplotlib properly supports pyside6

# from matplotlib.backends.backend_qt5agg import (  # noqa:E402
#    FigureCanvas,
#    NavigationToolbar2QT,
# )

# from pandas.plotting._matplotlib.boxplot import (  # noqa:F401,E402
#    LinePlot,
#    BoxPlot,
#    boxplot,
#    boxplot_frame,
#    boxplot_frame_groupby,
# )
# from pandas.plotting._matplotlib.converter import (  # noqa:F401,E402
#    deregister,
#    register,
# )


# from pandas.plotting._matplotlib.tools import table  # noqa:F401,E402

# from pandas.plotting._matplotlib.hist import (  # noqa:F401,E402
#    HistPlot,
#    KdePlot,
#    hist_frame,
#    hist_series,
# )

# from pandas.plotting._matplotlib.misc import (  # noqa:F401,E402
#    andrews_curves,
#    autocorrelation_plot,
#    bootstrap_plot,
#    lag_plot,
#    parallel_coordinates,
#    radviz,
#    scatter_matrix,
# )


# class BarPlot(LinePlot):
#    pass


# class BarhPlot(LinePlot):
#    pass


# class AreaPlot(LinePlot):
#    pass


# class PiePlot(LinePlot):
#    pass


# class ScatterPlot(LinePlot):
#    pass


# class HexBinPlot(LinePlot):
#    pass


PLOT_CLASSES = {"line": pgLinePlot}
PLOT_CLASSES_FALLBACK = {
    # remove fallbacks until matplotlib properly supports pyside6
    #    "line": LinePlot,
    #    "bar": BarPlot,
    #    "barh": BarhPlot,
    #    "box": BoxPlot,
    #    "hist": HistPlot,
    #    "kde": KdePlot,
    #    "area": AreaPlot,
    #    "pie": PiePlot,
    #    "scatter": ScatterPlot,
    #    "hexbin": HexBinPlot,
}


def plot(data, kind, **kwargs):
    fb = kwargs.pop("_fallbackBackend", False)
    # check if the plot kind is specified in the dataframe metadata.
    # if so, use the kind specified in the metadata
    # if not, use the kind passed to this fcn
    kind = data.attrs.get("plot.kind", kind)
    available = kind in PLOT_CLASSES
    _ = pg.mkQApp()
    if available and not fb:
        return PLOT_CLASSES[kind](data, **kwargs)
    else:
        kwargs.pop("x")
        kwargs.pop("y")
        W = QtWidgets.QWidget()

        # remove fallbacks until matplotlib properly supports pyside6
        # W.plot_obj = PLOT_CLASSES_FALLBACK[kind](data, **kwargs)
        # W.plot_obj.generate()
        # W.plot_obj.draw()

        # x = W.plot_obj.result
        # L = QtWidgets.QVBoxLayout()
        # W.setLayout(L)
        # L.setContentsMargins(0, 0, 0, 0)
        # L.setSpacing(0)
        # C = FigureCanvas(x.figure)
        # TB = NavigationToolbar2QT(C, W)
        # L.addWidget(TB)
        # L.addWidget(C)

        return W


# we add the entry point dynamically, so it also works in editable mode:
# https://stackoverflow.com/a/48666503
def _addEntryPoint():
    import pkg_resources

    d = pkg_resources.Distribution(__file__)
    ep = pkg_resources.EntryPoint.parse("dfplt = dfplt.backends:pg", dist=d)
    d._ep_map = {"pandas_plotting_backends": {"pg": ep}}
    pkg_resources.working_set.add(d, "pg")


_addEntryPoint()
