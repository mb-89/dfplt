import pyqtgraph as pg
import numpy as np
from functools import partial
from scipy import fft
from pyqtgraph import functions as fn
from scipy import signal

numValLen = 8
alpha = 255
blackforeground = pg.mkPen(0, 0, 0, alpha)
blackbackground = pg.mkBrush(48, 48, 48, alpha)

whiteforeground = pg.mkPen(0, 0, 0, alpha)
whitebackground = pg.mkBrush(178, 177, 179, alpha)


def getFixedLenString(flt, L=numValLen):

    s = np.format_float_scientific(flt, precision=L - 5, trim="-")
    return s


class RelPosLinearRegion(pg.LinearRegionItem):
    def __init__(self, parent, blackBg, updatefun):
        super().__init__()
        self.currRelRegion = [0.25, 0.75]
        self.updatefun = updatefun
        self.plt = parent
        self.setVisible(False)
        parent.addItem(self)
        self.sigRegionChanged.connect(self.callupdatefun)
        self.sigRegionChanged.connect(self.updateRelRegion)

    def callupdatefun(self, reg):
        try:
            if self.updatefun and self.isVisible():
                self.updatefun(reg)
        except RuntimeError:  # pragma: no cover
            pass  # this can happen on destruction

    def setVisible(self, vis):
        if vis and not self.isVisible():
            ((x0, x1), (y0, y1)) = self.plt.viewRange()
            self.setRelRegion([0.25, 0.75])
        super().setVisible(vis)

    def updateRelRegion(self, _):
        reg = self.getRegion()
        x0, x1 = self.getViewBox().viewRange()[0]
        dx = x1 - x0
        self.currRelRegion = [(reg[0] - x0) / dx, (reg[1] - x0) / dx]

    def setRelRegion(self, relRegion=None):
        if relRegion is None:
            relRegion = self.currRelRegion
        x0, x1 = self.plt.viewRange()[0]
        dx = x1 - x0
        self.setRegion([x0 + dx * relRegion[0], x0 + dx * relRegion[1]])

    def setRegion(self, reg):
        x0, x1 = self.getViewBox().viewRange()[0]
        dx = x1 - x0
        self.currRelRegion = [(reg[0] - x0) / dx, (reg[1] - x0) / dx]
        super().setRegion(reg)

    def viewTransformChanged(self):
        self.setRelRegion()
        fn = partial(self.callupdatefun, self)
        pg.QtCore.QTimer.singleShot(0, fn)
        return super().viewTransformChanged()


class pgPlotWithCursors(pg.PlotItem):
    roiChanged = pg.QtCore.Signal(object)

    def __init__(self, data, parent, kwargs):
        super().__init__()
        xdata = data.index.values
        xname = data.index.name if data.index.name else "idx"
        self.showGrid(1, 1, int(0.75 * alpha))
        black = parent.bgBlack
        self.black = black
        self.customlegend = pgLegendWithVals(
            xname,
            pen=blackforeground if black else whiteforeground,
            brush=blackbackground if black else whitebackground,
            offset=(70, 20),
        )
        self.customlegend.setParentItem(self)
        self.customlegend.setZValue(9999)
        self.addCursors(black)
        self.addROI(black)

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

    def addROI(self, black):
        self.roi = RelPosLinearRegion(self, black, self.roiChanged.emit)
        self.roi.setRelRegion((0.4, 0.6))
        self.roi.setVisible(False)
        # self.roi.setZValue(-9999)

    def addCursors(self, blackBG):
        self.c1 = pgRelPosCursor(1 / 3, label="C1", blackBg=blackBG)
        self.c2 = pgRelPosCursor(2 / 3, label="C2", blackBg=blackBG)
        self.addItem(self.c1)
        self.addItem(self.c2)
        self.c1.setZValue(9999)
        self.c2.setZValue(9999)
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
    def __init__(self, startposrel, blackBg=True, vertical=False, label=None):
        super().__init__(
            angle=90 if not vertical else 0,
            movable=True,
            label=label,
            labelOpts={"position": 0.95, "color": "yellow" if blackBg else "red"},
            pen="yellow" if blackBg else "red",
            hoverPen="yellow" if not blackBg else "red",
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


class FFTsubplot(pgPlotWithCursors):
    def __init__(self, src):
        pg.PlotItem.__init__(self)
        xname = "ℱ{" + src.plt.axes["bottom"]["item"].label.toPlainText().strip() + "}"
        self.setLabel("bottom", xname)
        self.setTitle("FFT")
        black = src.plt.black
        self.customlegend = pgLegendWithVals(
            xname,
            pen=blackforeground if black else whiteforeground,
            brush=blackbackground if black else whitebackground,
            offset=(70, 20),
        )
        self.customlegend.setParentItem(self)
        self.customlegend.setZValue(9999)
        self.customlegend.layout.itemAt(1, 1).setText(xname)
        self.addCursors(black)
        srccurves = src.plt.curves
        L = len(srccurves)
        self.showGrid(1, 1, int(0.75 * alpha))
        for idx, cu in enumerate(srccurves):
            self.plot(x=[0, 1], y=[0, 1], name=cu.name(), pen=(idx + 1, L))
        self.src = src

    def updateRange(self, roi):
        x0, x1 = roi.getRegion()

        xname = self.src.plt.axes["bottom"]["item"].label.toPlainText()
        s0 = getFixedLenString(x0, 6)
        s1 = getFixedLenString(x1, 6)
        self.setTitle(f"FFT on {xname}: {s0} -- {s1}")

        for idx, curve in enumerate(self.src.plt.curves):
            x = curve.xData
            y = curve.yData
            mask = np.logical_and(x >= x0, x <= x1)
            x = x[mask]
            y = y[mask]
            N = len(x)
            try:
                T = (x[-1] - x[0]) / N
            except IndexError:
                continue
            yf = 2.0 / N * np.abs(fft.fft(y)[0 : N // 2])
            xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
            self.curves[idx].setData(x=xf[1:], y=yf[1:])


class SpecImageItem(pg.ImageItem):
    geometryChanged = pg.QtCore.Signal()


class Specsubplot(pg.graphicsItems.GraphicsLayout.GraphicsLayout):
    winlenbase = 256
    winlenmaxrel = 8
    redrawSig = pg.QtCore.Signal()

    def __init__(self, src):
        super().__init__()
        self.src = src
        self.Sxx = None
        self.range = [0, 0]
        self.calcbusy = False
        # view = self.addViewBox(row=1, col=1)
        # view.setAspectLocked(True)
        self.pi = self.addPlot(row=1, col=1)
        self.pi.setTitle("Spec")
        self.pi.setLabel("bottom", "freq")
        self.pi.setLabel("left", "time")
        self.img = pg.ImageItem()
        self.pi.addItem(self.img)
        # view.addItem(self.pi)
        self.addItem(self.buildHist(), row=0, col=1)
        self.redrawproxy = pg.SignalProxy(
            self.redrawSig, rateLimit=3, slot=self._redraw
        )
        self.pi.getViewBox().invertY(True)
        self.addCursors(False)
        self.layout.setRowStretchFactor(1, 7)
        self.layout.setColumnStretchFactor(1, 7)
        self.target.setVisible(False)

    def addCursors(self, blackBG):
        self.ch = pgRelPosCursor(
            1 / 3, label="{value:0.2f} (A)", vertical=False, blackBg=blackBG
        )
        self.cv = pgRelPosCursor(
            2 / 3, label="{value:0.2f} (B)", vertical=True, blackBg=blackBG
        )
        self.pi.addItem(self.ch)
        self.pi.addItem(self.cv)
        self.ch.setZValue(9999)
        self.cv.setZValue(9999)
        self.cursors = dict((idx, c) for idx, c in enumerate([self.ch, self.cv]))
        self.proxies = [
            pg.SignalProxy(
                c.sigPositionChanged, rateLimit=60, slot=self.updateCursorVals
            )
            for c in self.cursors.values()
        ]
        for k, v in self.cursors.items():
            v.idx = k
        self.target = pg.TargetItem(
            pos=(self.cv.value(), self.ch.value()),
            size=0,
            label=self.getZ,
            labelOpts={"offset": (20, -20), "color": "red"},
        )
        self.pi.addItem(self.target)
        self.xsection = self.addPlot(row=2, col=1)
        self.ysection = self.addPlot(row=1, col=0)

        self.xsection.setTitle("z vals along (B)")
        self.ysection.setTitle("z vals along (A)")
        self.xsection.setLabel("bottom", "freq")
        self.xsection.setLabel("left", "z")
        self.xsection.setXLink(self.pi)
        self.ysection.setYLink(self.pi)
        self.ysection.setLabel("bottom", "z")
        self.ysection.setLabel("left", "time")
        self.xsection.setVisible(False)
        self.ysection.setVisible(False)

    def _redraw(self):
        y0, y1 = self.range
        dy = y1 - y0
        if not dy:
            return
        calcDone = self.calc()
        if not calcDone:
            return

        self.img.setImage(self.Sxx)
        self.img.resetTransform()

        y0, y1 = self.range
        dy = y1 - y0
        x0, dx = self.f[0], self.f[-1]

        self.img.setRect(pg.QtCore.QRectF(x0, y0, dx, dy))
        self.hist.setLevels(np.min(self.Sxx), np.percentile(self.Sxx, 99))
        for x in self.pi.axes:
            ax = self.pi.getAxis(x)
            ax.setZValue(1)
        self.pi.setLimits(yMin=y0, yMax=y0 + dy, xMin=y0, xMax=x0 + dx)

    def calc(self):
        if self.calcbusy:
            return False
        self.calcbusy = True

        range = self.range
        col = self.src.plt.curves[0]
        Y = col.yData
        T = col.xData
        mask = np.logical_and(T >= range[0], T <= range[1])
        T = T[mask]
        Y = Y[mask]
        L = len(T)
        newt0t1 = [T[0], T[-1]]
        self.range = newt0t1
        self.fs = (T[-1] - T[0]) / len(T)

        self.f, self.t, self.Sxx = signal.spectrogram(
            Y,
            1 / ((T[-1] - T[0]) / L),
            scaling="spectrum",
            mode="magnitude",
            nperseg=self.winlenbase * 4,
        )
        self.Sxx *= 2.0

        self.calcbusy = False
        return True

    def updateRange(self, roi):
        self.range = roi.getRegion()
        self.redrawSig.emit()

    def toggleCursors(self, tgl):
        for k, v in self.cursors.items():
            v.setVisible(tgl)
        self.xsection.setVisible(tgl)
        self.ysection.setVisible(tgl)
        self.target.setVisible(tgl)

    def buildHist(self):
        self.hist = HoriHist()
        self.hist.setImageItem(self.img)
        return self.hist

    def getZ(self, x, y):
        if self.Sxx is None:
            return
        xrel = min(np.searchsorted(self.f, x), len(self.f) - 1)
        yrel = min(np.searchsorted(self.t, y - self.range[0]), len(self.t) - 1)
        zval = self.Sxx[xrel, yrel]

        self.xsection.clear()
        self.xsection.plot(x=self.f, y=self.Sxx[:, yrel])
        self.xsection.setLimits(xMin=0, xMax=self.f[-1])
        self.ysection.clear()
        self.ysection.plot(y=self.t + self.range[0], x=self.Sxx[xrel, :])
        self.ysection.setLimits(yMin=self.range[0], yMax=self.range[1])
        self.ysection.getViewBox().invertY(True)
        return f"z: {zval:.2f}"

    def updateCursorVals(self, c):
        self.target.setPos((self.ch.value(), self.cv.value()))


class HoriHist(pg.HistogramLUTItem):
    def __init__(
        self, image=None, fillHistogram=True, rgbHistogram=False, levelMode="mono"
    ):
        pg.GraphicsWidget.__init__(self)
        self.lut = None
        self.imageItem = lambda: None  # fake a dead weakref
        self.levelMode = levelMode
        self.rgbHistogram = rgbHistogram

        self.layout = pg.QtWidgets.QGraphicsGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        self.vb = pg.ViewBox(parent=self)
        self.vb.setMaximumHeight(20)
        self.vb.setMinimumHeight(20)
        self.vb.setMouseEnabled(x=False, y=True)

        self.gradient = pg.GradientEditorItem()
        self.gradient.setOrientation("top")
        self.gradient.loadPreset("viridis")

        self.gradient.setFlag(self.gradient.ItemStacksBehindParent)
        self.vb.setFlag(self.gradient.ItemStacksBehindParent)
        self.layout.addItem(self.gradient, 0, 0)
        self.layout.addItem(self.vb, 1, 0)
        self.axis = pg.AxisItem(
            "bottom", linkView=self.vb, maxTickLength=-10, parent=self
        )
        self.layout.addItem(self.axis, 2, 0)

        self.regions = [pg.LinearRegionItem([0, 1], "vertical", swapMode="block")]
        for region in self.regions:
            region.setZValue(1000)
            self.vb.addItem(region)
            region.lines[0].addMarker("<|", 0.5)
            region.lines[1].addMarker("|>", 0.5)
            region.sigRegionChanged.connect(self.regionChanging)
            region.sigRegionChangeFinished.connect(self.regionChanged)
        self.region = self.regions[0]

        add = pg.QtGui.QPainter.CompositionMode_Plus
        self.plots = [
            pg.PlotCurveItem(pen=(200, 200, 200, 100)),  # mono
            pg.PlotCurveItem(pen=(255, 0, 0, 100), compositionMode=add),  # r
            pg.PlotCurveItem(pen=(0, 255, 0, 100), compositionMode=add),  # g
            pg.PlotCurveItem(pen=(0, 0, 255, 100), compositionMode=add),  # b
            pg.PlotCurveItem(pen=(200, 200, 200, 100), compositionMode=add),  # a
        ]
        self.plot = self.plots[0]
        for plot in self.plots:
            self.vb.addItem(plot)
        self.fillHistogram(fillHistogram)

        self.range = None
        self.gradient.sigGradientChanged.connect(self.gradientChanged)
        self.vb.sigRangeChanged.connect(self.viewRangeChanged)

    def paint(self, p, *args):
        if self.levelMode != "mono":
            return

        pen = self.region.lines[0].pen
        rgn = self.getLevels()
        p1 = self.vb.mapFromViewToItem(
            self, pg.Point(rgn[0], self.vb.viewRect().center().y())
        )
        p2 = self.vb.mapFromViewToItem(
            self, pg.Point(rgn[1], self.vb.viewRect().center().y())
        )
        gradRect = self.gradient.mapRectToParent(self.gradient.gradRect.rect())
        p.setRenderHint(pg.QtGui.QPainter.Antialiasing)
        for pen in [fn.mkPen((0, 0, 0, 100), width=3), pen]:
            p.setPen(pen)
            p.drawLine(p1 - pg.Point(5, 0), gradRect.bottomLeft())
            p.drawLine(p2 + pg.Point(5, 0), gradRect.bottomRight())
            p.drawLine(gradRect.topLeft(), gradRect.bottomLeft())
            p.drawLine(gradRect.topRight(), gradRect.bottomRight())
