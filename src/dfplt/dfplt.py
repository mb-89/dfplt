# we need this import so that the backend gets registered
from dfplt import backends  # noqa: F401

import argparse
from .__metadata__ import __version__
from pyqtgraph.Qt import QtWidgets, QtCore, mkQApp
import itertools
import matplotlib
from matplotlib import axes
import PySide6  # noqa:F401 we need this so its added to the requirements.txt


def main(argv):
    parser = argparse.ArgumentParser(
        "parses given glob-style paths and plots any found dataframes."
        + " Plots all the given dataframes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("srcs", nargs="*", help="glob-style paths that will be parsed")
    parser.add_argument(
        "-?", action="store_true", help="show this help message and exit"
    )
    parser.add_argument(
        "--nonblock",
        action="store_true",
        help="set to true to open figures in nonblocking mode for debugging "
        + "or batch exports.",
    )

    parser.add_argument("-v", "--version", action="store_true", help="prints version")
    args = argv[1:]
    args = vars(parser.parse_args(args))

    if args["version"]:
        print(__version__)
        return 0
    if args["?"] or not args["srcs"]:
        parser.print_help()
        return 0

    # we only need x2df for the commandline interface.
    from x2df import x2df

    dfs = itertools.chain.from_iterable(x2df.load(src) for src in args["srcs"])

    plots = (plot(df) for df in dfs)
    plots = [x for x in plots if x]

    if not plots:
        parser.print_help()
        return 0

    show(plots, block=not args["nonblock"])

    return 0


def plot(df):
    return df.plot()


def show(plots, block=True):
    anyMatPlotLib = any(isinstance(x, axes._subplots.SubplotBase) for x in plots)
    if anyMatPlotLib:
        matplotlib.pyplot.show(block=block)

    widgets = [x for x in plots if isinstance(x, QtWidgets.QWidget)]
    if widgets:
        app = mkQApp()
        if not block:
            QtCore.QTimer.singleShot(100, app.quit)
        for w in widgets:
            w.show()
        app.exec()
