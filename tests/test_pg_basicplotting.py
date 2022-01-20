from dfplt import examplegallery, dfplt
from pyqtgraph.Qt import QtCore, mkQApp
from dfplt.backends.pg.lineplot import Lineplot


def test_fallback(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("matplotlib")
    for example in eg.availableExamples:
        eg.ex.setCurrentText(example)


def test_plotting_via_main(qtbot):
    app = mkQApp()

    def closewin():
        plt = [x for x in app.topLevelWidgets() if isinstance(x, Lineplot)][0]
        qtbot.addWidget(plt)
        plt.close()

    QtCore.QTimer.singleShot(0, closewin)
    dfplt.main(["test", "example_stepresponses1"])


def test_plotting_df_directly(qtbot):
    dfs = dfplt.load("example_stepresponses1")
    w = dfplt.plot(dfs[0])
    assert dfs
    app = mkQApp()

    def closewin():
        plt = [x for x in app.topLevelWidgets() if isinstance(x, Lineplot)][0]
        qtbot.addWidget(plt)
        plt.close()

    QtCore.QTimer.singleShot(0, closewin)
    dfplt.show(w)
