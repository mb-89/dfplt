from dfplt import examplegallery, dfplt
from pyqtgraph.Qt import QtCore, mkQApp


def test_fallback(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("matplotlib")
    for example in eg.availableExamples:
        eg.ex.setCurrentText(example)


def test_plotting_via_main(qtbot):
    app = mkQApp()
    t = QtCore.QTimer()
    t.setInterval(100)
    t.timeout.connect(app.exit)  # do it like this bc we cant rely on timing
    t.start()
    dfplt.main(["test", "example_stepresponses1"])


def test_plotting_df_directly(qtbot):
    dfs = dfplt.load("example_stepresponses1")
    w = dfplt.plot(dfs[0])
    assert dfs
    app = mkQApp()
    t = QtCore.QTimer()
    t.setInterval(100)
    t.timeout.connect(app.exit)  # do it like this bc we cant rely on timing
    t.start()
    dfplt.show(w)
