from dfplt import examplegallery
from pyqtgraph.Qt import QtCore


def test_showspec(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    # open the spec plot
    qtbot.mouseClick(eg.plt.specButton, QtCore.Qt.MouseButton.LeftButton)
    subplt = eg.plt.mainPlot.ci.rows.get(1, {}).get(0)
    assert subplt.pi.titleLabel.text.startswith("Spec")

    # drag the screen so the cursor values and roi get updated
    qtbot.mousePress(eg.plt.mainPlot, QtCore.Qt.LeftButton, pos=QtCore.QPoint(50, 50))
    qtbot.mouseMove(eg.plt.mainPlot, pos=QtCore.QPoint(100, 100))
    qtbot.mouseRelease(eg.plt.mainPlot, QtCore.Qt.LeftButton)
    qtbot.wait(100)

    # open the cursors
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    # TODO: Add legend to spec
    # assert subplt.pi.customlegend.expanded

    # switch to white bg and open spec again
    qtbot.mouseClick(eg.plt.bwButton, QtCore.Qt.MouseButton.LeftButton)
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    qtbot.mouseClick(eg.plt.specButton, QtCore.Qt.MouseButton.LeftButton)
    subplt = eg.plt.mainPlot.ci.rows.get(1, {}).get(0)
    assert not subplt.src.plt.black

    # test div/0
    subplt.src.plt.roi.setRelRegion((0.3, 0.3))  # test div/0
    qtbot.wait(100)


def test_calcTooFast(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    # open the spec plot
    qtbot.mouseClick(eg.plt.specButton, QtCore.Qt.MouseButton.LeftButton)
    subplt = eg.plt.mainPlot.ci.rows.get(1, {}).get(0)
    qtbot.wait(100)
    subplt.src.plt.roi.setRelRegion((0.2, 0.4))  # test div/0
    qtbot.wait(100)
    # call the calc function too fast:
    subplt.calcbusy = True
    subplt._redraw()
    qtbot.wait(100)


def test_specCursors(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    # open the spec plot, move the cursor
    qtbot.mouseClick(eg.plt.specButton, QtCore.Qt.MouseButton.LeftButton)
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    qtbot.wait(100)
    subplt = eg.plt.mainPlot.ci.rows.get(1, {}).get(0)
    subplt.ch.setRelPos(0.7)
    qtbot.wait(100)


def test_specMoveHistLine(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.show()
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    # open the spec plot, move the hist cursor
    qtbot.mouseClick(eg.plt.specButton, QtCore.Qt.MouseButton.LeftButton)
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    qtbot.wait(100)
    subplt = eg.plt.mainPlot.ci.rows.get(1, {}).get(0)
    line = subplt.hist.regions[0].lines[1]
    line.setPos(line.pos() + (0.5, 0))
    qtbot.wait(100)
    subplt.hist.levelMode = "notMono"  # just to test the edge case
    line.setPos(line.pos() + (0.5, 0))
    qtbot.wait(100)
