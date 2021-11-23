import pyqtgraph as pg


class plotWidget(pg.Qt.QtWidgets.QWidget):
    def __init__(self, data, **kwargs):
        super().__init__()
