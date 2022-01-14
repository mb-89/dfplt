from dfplt import examplegallery

# we need this import so that the backend gets registered
from dfplt import backends  # noqa: F401

import argparse
from .__metadata__ import __version__
from pyqtgraph.Qt import QtWidgets, QtCore, mkQApp
import itertools
from pandas import DataFrame
from collections.abc import Iterable

import PySide6  # noqa:F401 we need this so its added to the requirements.txt

from IPython import get_ipython

ipython = get_ipython()
if ipython:
    ipython.run_line_magic("gui", "qt")


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
    parser.add_argument(
        "--examples", action="store_true", help="shows the example gallery"
    )
    args = argv[1:]
    args = vars(parser.parse_args(args))

    if args["version"]:
        print(__version__)
        return 0
    if args["examples"]:
        app = mkQApp()
        w = QtWidgets.QMainWindow()
        w.setCentralWidget(examplegallery.Examplegallery())
        w.resize(600, 400)
        if args["nonblock"]:
            QtCore.QTimer.singleShot(100, app.quit)
        w.show()
        return app.exec()
    if args["?"] or not args["srcs"]:
        parser.print_help()
        return 0

    plots = plot(args["srcs"])

    if not plots:
        parser.print_help()
        return 0

    show(plots, block=not args["nonblock"])

    return 0


def load(srcs):
    from x2df import x2df

    if isinstance(srcs, str) or not isinstance(srcs, Iterable):
        srcs = [srcs]
    dfs = list(itertools.chain.from_iterable(x2df.load(src) for src in srcs))
    return dfs


def plot(dfOrSrc):
    if isinstance(dfOrSrc, DataFrame):
        return dfOrSrc.plot()
    # if we are here, the input was not a dataframe:
    dfs = load([dfOrSrc])
    plots = (plot(df) for df in dfs)
    plots = [x for x in plots if x]
    return plots


def show(plots, block=True):
    widgets = [x for x in plots if isinstance(x, QtWidgets.QWidget)]
    if widgets:
        if ipython:
            for w in widgets:
                w.show()
            return

        app = mkQApp()
        if not block:
            QtCore.QTimer.singleShot(100, app.quit)
        for w in widgets:
            w.show()
        app.exec()
