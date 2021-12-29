from pyqtgraph.Qt import QtWidgets, QtCore
from x2df import x2df
from dfplt.backends import getAvailableBackends


class Examplegallery(QtWidgets.QWidget):
    plotReady = QtCore.Signal()

    def __init__(self):
        super().__init__()
        la = QtWidgets.QHBoxLayout()
        la.setContentsMargins(0, 0, 0, 0)
        la.setSpacing(0)

        backendSelector = QtWidgets.QComboBox()
        exampleSelector = QtWidgets.QComboBox()

        # add matplotlib as a placeholder until
        # it supports pyside6 and we can use it properly
        self.availableBackends = [x for x in getAvailableBackends()] + ["matplotlib"]
        self.availableExamples = [x for x in x2df.getExampleNames()]

        backendSelector.addItems(self.availableBackends)
        exampleSelector.addItems(self.availableExamples)
        backendSelector.currentIndexChanged.connect(self.plot)
        exampleSelector.currentIndexChanged.connect(self.plot)

        la.addWidget(backendSelector)
        la.addWidget(exampleSelector)

        l2 = QtWidgets.QVBoxLayout()
        l2.setContentsMargins(0, 0, 0, 0)
        l2.setSpacing(0)

        l2.addLayout(la)

        self.setLayout(l2)
        self.ex = exampleSelector
        self.be = backendSelector
        self.plt = None

        QtCore.QTimer.singleShot(0, self.plot)

    def plot(self, _=None):
        examplename = self.ex.currentText()
        backend = self.be.currentText()

        dfs = x2df.load(examplename)

        # matplotlib plots into dedicated windows by default.
        # we dont want that here, we want the widget and embed it.
        # so we need to use this trick:
        fallback = False
        if backend == "matplotlib":
            backend = "dfplt"
            fallback = True

        w = dfs[0].plot(backend=backend, _fallbackBackend=fallback)
        la = self.layout()
        if self.plt:
            self.plt.setHidden(True)
            la.removeWidget(self.plt)
            self.plt.deleteLater()
            self.plt = None
        self.plt = w
        la.addWidget(w)
        self.plotReady.emit()
