from dfplt.backends.pg.common import plotWidget
from dfplt.backends.pg.plotElements import pgPlotWithCursors, FFTsubplot
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from functools import partial
import tempfile
import os.path as op
from IPython.display import Image, display
from IPython import get_ipython


ipython = get_ipython()
if ipython:  # pragma: no cover #dont know how to test this yet
    ipython.run_line_magic("gui", "qt")


class Lineplot(plotWidget):
    cursorToggle = QtCore.Signal(bool)

    def __init__(self, data, **kwargs):
        super().__init__(data)
        la = QtWidgets.QVBoxLayout()
        la.setSpacing(0)
        la.setContentsMargins(0, 0, 0, 0)
        self.setLayout(la)
        self.bgBlack = True
        pg.setConfigOption("background", "k")
        pg.setConfigOption("foreground", "w")
        self.mainPlotFun = partial(pgLineplot, data, self, kwargs)

        self.toolbar = QtWidgets.QHBoxLayout()
        self.toolbar.setSpacing(0)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.toolbar.addStretch()

        la.addLayout(self.toolbar)

        self.addButtons()
        self.drawPlt()

    def drawPlt(self):
        la = self.layout()
        if la.count() > 1:
            self.mainPlot.hide()
            la.removeWidget(self.mainPlot)
            self.mainPlot.deleteLater()

        self.mainPlot = self.mainPlotFun()
        la.addWidget(self.mainPlot)
        self.toggleCursors(False)

    def addButtons(self):
        self.addCursButton()
        self.addBWButton()
        self.addCpyButton()
        self.addFFTButton()

    def addBWButton(self):
        self.bwButton = QtWidgets.QPushButton("BW")
        self.bwButton.setMaximumWidth(35)
        self.bwButton.setCheckable(True)
        self.bwButton.toggled.connect(self.toggleBW)
        self.toolbar.addWidget(self.bwButton)

    def addCursButton(self):
        self.cursorButton = QtWidgets.QPushButton("Cu")
        self.cursorButton.setMaximumWidth(35)
        self.cursorButton.setCheckable(True)
        self.cursorButton.toggled.connect(self.toggleCursors)
        self.toolbar.addWidget(self.cursorButton)

    def addCpyButton(self):
        self.cpyButton = QtWidgets.QPushButton("Cp")
        self.cpyButton.setMaximumWidth(35)
        self.cpyButton.clicked.connect(self.toClipboard)
        self.toolbar.addWidget(self.cpyButton)

    def addFFTButton(self):
        self.fftButton = QtWidgets.QPushButton("fft")
        self.fftButton.setMaximumWidth(50)
        self.fftButton.setCheckable(True)
        self.fftButton.toggled.connect(self.toggleFFT)
        self.toolbar.addWidget(self.fftButton)

    def toggleFFT(self, newtglval):
        self.destroySubplot()
        self.mainPlot.setROIvisible(newtglval)
        if not newtglval:
            return
        self.mainPlot.ci.layout.setRowStretchFactor(1, 2)
        fftplot = FFTsubplot(self.mainPlot)
        self.mainPlot.addItem(fftplot, row=1, col=0)

    def destroySubplot(self):
        existingPlot = self.mainPlot.ci.rows.get(1, {}).get(0)
        if existingPlot:
            self.mainPlot.ci.layout.setRowStretchFactor(1, 0)
            existingPlot.setVisible(False)
            existingPlot.deleteLater()
            self.mainPlot.ci.removeItem(existingPlot)

    def toggleCursors(self, tgl):
        self.mainPlot.toggleCursors(tgl)
        existingSubPlot = self.mainPlot.ci.rows.get(1, {}).get(0)
        if existingSubPlot:
            existingSubPlot.toggleCursors(tgl)
        self.cursorToggle.emit(tgl)

    def toClipboard(self):
        self.mainPlot.toClipboard()

    def toggleBW(self):
        setWhite = self.bgBlack
        self.bgBlack = not self.bgBlack
        pg.setConfigOption("background", "w" if setWhite else "k")
        pg.setConfigOption("foreground", "k" if setWhite else "w")
        self.cursorButton.setChecked(False)
        self.fftButton.setChecked(False)
        self.drawPlt()

    def mainROIchanged(self, roi):
        existingSubPlot = self.mainPlot.ci.rows.get(1, {}).get(0)
        if existingSubPlot:
            existingSubPlot.updateRange(roi)


class pgLineplot(pg.GraphicsLayoutWidget):
    def __init__(self, data, parent, kwargs):
        super().__init__()
        self.plt = pgPlotWithCursors(data, parent, kwargs)
        self.addItem(self.plt, row=0, col=0)
        self.plt.roiChanged.connect(parent.mainROIchanged)
        self.ci.layout.setRowStretchFactor(0, 1)
        self.ci.layout.setRowStretchFactor(1, 0)

    def toggleCursors(self, tgl):
        self.plt.toggleCursors(tgl)

    def toClipboard(self):
        pix = self.grab()
        pg.mkQApp().clipboard().setPixmap(pix)
        if ipython:  # pragma: no cover #no idea how to test this yet
            with tempfile.TemporaryDirectory() as td:
                path = op.join(td, "tmp.png")
                pix.save(path, "PNG")
                display(Image(filename=path))

    def setROIvisible(self, vis):
        self.plt.roi.setVisible(vis)
