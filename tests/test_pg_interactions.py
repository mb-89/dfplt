from dfplt import examplegallery
from pyqtgraph.Qt import QtCore


def test_lineplot_zoom_pan_cursors(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    # open the cursors
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    assert eg.plt.mainPlot.plt.customlegend.expanded

    # open when already opened to catch edge case and check that it doesnt crash
    eg.plt.mainPlot.plt.customlegend.addCursorCols()

    # drag the screen so the cursor values get updated
    qtbot.mousePress(eg.plt.mainPlot, QtCore.Qt.LeftButton, pos=QtCore.QPoint(50, 50))
    qtbot.mouseMove(eg.plt.mainPlot, pos=QtCore.QPoint(100, 100))
    qtbot.mouseRelease(eg.plt.mainPlot, QtCore.Qt.LeftButton)
    qtbot.wait(100)

    # drag the screen very far,
    # and check that this is caught properly
    eg.plt.mainPlot.plt.cursors[0].setRelPos(-1)
    qtbot.wait(100)
    eg.plt.mainPlot.plt.cursors[0].setRelPos(2)

    # close the cursors
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    assert not eg.plt.mainPlot.plt.customlegend.expanded

    # close when already close to catch edge case and check that it doesnt crash
    eg.plt.mainPlot.plt.customlegend.remCursorCols()

    # open the cursors a 2nd time for coverage
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    assert eg.plt.mainPlot.plt.customlegend.expanded


def test_blackwhite(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    qtbot.mouseClick(eg.plt.bwButton, QtCore.Qt.MouseButton.LeftButton)
    assert not eg.plt.bgBlack


def test_copy(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    qtbot.mouseClick(eg.plt.cpyButton, QtCore.Qt.MouseButton.LeftButton)
    # only click it to see that we have no exceptions
