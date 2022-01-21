from dfplt import examplegallery
from pyqtgraph.Qt import QtCore


def test_showfft(qtbot):
    eg = examplegallery.Examplegallery()
    qtbot.addWidget(eg)
    eg.be.setCurrentText("dfplt")
    with qtbot.waitSignal(eg.plotReady) as _:
        eg.ex.setCurrentText("examples_stepresponse1")

    # open the fft plot
    qtbot.mouseClick(eg.plt.fftButton, QtCore.Qt.MouseButton.LeftButton)
    subplt = eg.plt.mainPlot.ci.rows.get(1, {}).get(0)
    assert subplt.titleLabel.text.startswith("FFT")

    # drag the screen so the cursor values and roi get updated
    qtbot.mousePress(eg.plt.mainPlot, QtCore.Qt.LeftButton, pos=QtCore.QPoint(50, 50))
    qtbot.mouseMove(eg.plt.mainPlot, pos=QtCore.QPoint(100, 100))
    qtbot.mouseRelease(eg.plt.mainPlot, QtCore.Qt.LeftButton)
    qtbot.wait(100)

    # open the cursors
    qtbot.mouseClick(eg.plt.cursorButton, QtCore.Qt.MouseButton.LeftButton)
    assert subplt.customlegend.expanded

    # switch to white bg and open fft again
    qtbot.mouseClick(eg.plt.bwButton, QtCore.Qt.MouseButton.LeftButton)
    qtbot.mouseClick(eg.plt.fftButton, QtCore.Qt.MouseButton.LeftButton)
    subplt = eg.plt.mainPlot.ci.rows.get(1, {}).get(0)
    assert not subplt.src.plt.black

    # test div/0
    subplt.src.plt.roi.setRelRegion((0.3, 0.3))  # test div/0
