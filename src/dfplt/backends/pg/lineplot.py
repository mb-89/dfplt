from dfplt.backends.pg.common import plotWidget
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
from functools import partial
import tempfile
import os.path as op
from IPython.display import Image, display
from IPython import get_ipython

numValLen = 8


def getFixedLenString(flt, L=numValLen):

    s = np.format_float_scientific(flt, precision=L - 5, trim="-")
    return s


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
        self.mainPlotFun = partial(pgLineplot, data, kwargs)

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

    def addBWButton(self):
        self.bwBlack = True
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

    def toggleCursors(self, tgl):
        self.mainPlot.toggleCursors(tgl)
        self.cursorToggle.emit(tgl)

    def toClipboard(self):
        self.mainPlot.toClipboard()

    def toggleBW(self):
        setWhite = self.bwBlack
        self.bwBlack = not self.bwBlack
        pg.setConfigOption("background", "w" if setWhite else "k")
        pg.setConfigOption("foreground", "k" if setWhite else "w")
        self.cursorButton.setDown(False)
        self.drawPlt()


class pgLineplot(pg.GraphicsLayoutWidget):
    def __init__(self, data, kwargs):
        super().__init__()
        self.plt = pgPlotWithCursors(data, kwargs)
        self.addItem(self.plt, row=0, col=0)

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


class pgPlotWithCursors(pg.PlotItem):
    def __init__(self, data, kwargs):
        super().__init__()
        A = 65
        xdata = data.index.values
        xname = data.index.name if data.index.name else "idx"
        self.showGrid(1, 1, int(0.75 * 255))
        self.customlegend = pgLegendWithVals(
            xname,
            pen=pg.mkPen(255, 255, 255, A),
            brush=pg.mkBrush(0, 0, 255, A),
            offset=(70, 20),
        )
        self.customlegend.setParentItem(self)
        self.addCursors()

        L = len(data.columns)
        self.setLabel("bottom", xname)
        for idx, yname in enumerate(data.columns):
            self.plot(
                x=xdata,
                y=data[yname],
                name=yname,
                pen=(idx + 1, L),
                autoDownsample=True,
                clipToView=True,
            )

    def toggleCursors(self, tgl):
        for k, v in self.cursors.items():
            v.setVisible(tgl)
        if tgl:
            self.customlegend.addCursorCols()
            for idx, c in enumerate(self.cursors.values()):
                pg.QtCore.QTimer.singleShot(0, partial(self.updateCursorVals, [c]))
        else:
            self.customlegend.remCursorCols()

    def addCursors(self):
        # if we have no plugins, the cursor btn is part of a different plot widget
        self.c1 = pgRelPosCursor(1 / 3, label="C1")
        self.c2 = pgRelPosCursor(2 / 3, label="C2")
        self.addItem(self.c1)
        self.addItem(self.c2)
        self.cursors = dict((idx, c) for idx, c in enumerate([self.c1, self.c2]))
        self.proxies = [
            pg.SignalProxy(
                c.sigPositionChanged, rateLimit=30, slot=self.updateCursorVals
            )
            for c in self.cursors.values()
        ]
        for k, v in self.cursors.items():
            v.idx = k

    def updateCursorVals(self, c):
        if not self.customlegend.expanded:
            return
        c = c[0]
        try:
            xval = c.pos()[0]
        except RuntimeError:  # pragma: no cover # can happen during debugging
            return
        tmp = [xval]
        for cuidx, cu in enumerate(self.curves):
            idx = np.searchsorted(cu.xData, xval, side="left")
            L = len(cu.yData)
            yval = cu.yData[max(0, min(idx, L - 1))]
            tmp.append(yval)
        self.customlegend.setVals(c.idx, tmp)

    def plot(self, *args, **kwargs):
        p = super().plot(*args, **kwargs)
        self.customlegend.addItem(p, kwargs.get("name", "unnamed"))
        return p


class pgLegendWithVals(pg.LegendItem):
    def __init__(self, xname, *args, **kwargs):
        kwargs["colCount"] = 1
        super().__init__(*args, **kwargs)
        self.layout.addItem(pg.LabelItem("Name"), 0, 1)
        self.layout.addItem(pg.LabelItem(" X"), 1, 0)
        self.layout.addItem(pg.LabelItem(xname), 1, 1)
        self.expanded = False
        self.w0 = None
        self.w1 = None

    def setVals(self, cursorIdx, vals):
        for vidx, v in enumerate(vals):
            targetItem = self.layout.itemAt(vidx + 1, cursorIdx + 2)
            targetItem._val = v

            targetItem.setText(getFixedLenString(v))
        if (
            self.layout.itemAt(1, 2)._val is not None
            and self.layout.itemAt(1, 3)._val is not None
        ):
            self.calcDerivativeVals()

    def calcDerivativeVals(self):
        for row in range(1, self.layout.rowCount()):
            v0 = self.layout.itemAt(row, 2)._val
            v1 = self.layout.itemAt(row, 3)._val
            delta = v1 - v0
            deltainv = 0 if delta == 0 else 1 / delta
            t = self.layout.itemAt(row, 4)
            t._val = delta
            t.setText(getFixedLenString(delta))
            t = self.layout.itemAt(row, 5)
            t._val = deltainv
            t.setText(getFixedLenString(deltainv))

    def _addItemToLayout(self, sample, label):
        col = self.layout.columnCount()
        row = self.layout.rowCount()
        # in the original code, the next two lines are not commented out
        # if row:
        #    row -= 1
        # we need this bc we injected more rows and cols than in the original code
        if row == 2:
            col = 0
        else:
            col = 2

        nCol = self.columnCount * 2

        for col in range(0, nCol, 2):
            # FIND RIGHT COLUMN
            # if i dont add the row>=...,  get QGraphicsGridLayout::itemAt errors
            if row >= self.layout.rowCount() or not self.layout.itemAt(row, col):
                break

        self.layout.addItem(sample, row, col)
        self.layout.addItem(label, row, col + 1)
        # Keep rowCount in sync with the number of rows if items are added
        self.rowCount = max(self.rowCount, row + 1)

    def addCursorCols(self):
        if self.expanded:
            return
        self.expanded = True
        if self.w0 is None:
            self.w0 = self.layout.geometry().width()

        self.layout.addItem(pg.LabelItem("C1"), 0, 2)
        self.layout.addItem(pg.LabelItem("C2"), 0, 3)
        self.layout.addItem(pg.LabelItem("Δ"), 0, 4)
        self.layout.addItem(pg.LabelItem("1/Δ"), 0, 5)

        for col in range(2, 6):
            self.layout.setColumnMaximumWidth(col, numValLen * 7)
            self.layout.setColumnMinimumWidth(col, numValLen * 7)

        if self.w1 is not None:
            self.setMaximumWidth(self.w1)

        for row in range(1, self.layout.rowCount()):
            for col in range(2, 6):
                item = pg.LabelItem("")
                item._val = None
                self.layout.addItem(item, row, col)

    def remCursorCols(self):
        if not self.expanded:
            return
        self.expanded = False
        if self.w1 is None:
            self.w1 = self.layout.geometry().width()

        for col in range(2, 6):
            item = self.layout.itemAt(0, col)
            item.setVisible(False)
            item.deleteLater()
            self.layout.removeItem(item)

        for row in range(1, self.layout.rowCount()):
            for col in range(2, 6):
                item = self.layout.itemAt(row, col)
                item.setVisible(False)
                item.deleteLater()
                self.layout.removeItem(item)

        if self.w0 is not None:
            self.setMaximumWidth(self.w0)


class pgRelPosCursor(pg.InfiniteLine):
    def __init__(self, startposrel, vertical=False, label=None):
        super().__init__(
            angle=90 if not vertical else 0,
            movable=True,
            label=label,
            labelOpts={"position": 0.95},
        )
        self.setVisible(False)
        self.startposrel = startposrel
        self.currposrel = startposrel
        self.vertical = vertical

    def setVisible(self, vis):
        if vis:
            self.setRelPos(self.startposrel)
        super().setVisible(vis)

    def setPos(self, pos):
        try:
            range = self.getViewBox().viewRange()
            x0, x1 = range[0] if not self.vertical else range[1]
            dx = x1 - x0
            self.currposrel = (pos - x0) / dx
        except AttributeError:
            pass
        super().setPos(pos)

    def setRelPos(self, relpos=None):
        if relpos is None:
            relpos = self.currposrel
        range = self.getViewBox().viewRange()
        x0, x1 = range[0] if not self.vertical else range[1]
        dx = x1 - x0
        self.setValue(x0 + relpos * dx)

    def viewTransformChanged(self):
        self.setRelPos()
        return super().viewTransformChanged()
