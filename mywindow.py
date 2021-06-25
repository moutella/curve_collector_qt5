from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from mycanvas import *
from mymodel import *


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass it to canvas object
        self.model = MyModel()
        self.canvas.setModel(self.model)
        # create a Toolbar
        tb = self.addToolBar("File")
        fit = QAction(QIcon("icons/fit.jpg"), "fit", self)
        tb.addAction(fit)

        # Pan
        panR = QAction(QIcon("icons/panright.jpg"), "panR", self)
        tb.addAction(panR)
        panL = QAction(QIcon("icons/panleft.jpg"), "panL", self)
        tb.addAction(panL)
        panU = QAction(QIcon("icons/panup.jpg"), "panU", self)
        tb.addAction(panU)
        panD = QAction(QIcon("icons/pandown.jpg"), "panD", self)
        tb.addAction(panD)

        # Zoom
        zoomIn = QAction(QIcon("icons/zoomin.jpg"), "zoomIn", self)
        tb.addAction(zoomIn)
        zoomOut = QAction(QIcon("icons/zoomout.jpg"), "zoomOut", self)
        tb.addAction(zoomOut)

        reset = QAction(QIcon("icons/zoomout.jpg"), "reset", self)
        tb.addAction(reset)

        tb.actionTriggered[QAction].connect(self.tbpressed)
#        tb2 = self.addToolBar("Draw")
#        line = QAction(QIcon("icons/fit.jpg"),"line",self)
#        tb2.addAction(line)

    def tbpressed(self, a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == 'panR':
            self.canvas.panWorldWindow(-0.2, 0)
        if a.text() == 'panL':
            self.canvas.panWorldWindow(0.2, 0)
        if a.text() == 'panU':
            self.canvas.panWorldWindow(0, -0.2)
        if a.text() == 'panD':
            self.canvas.panWorldWindow(0, 0.2)
        if a.text() == 'zoomIn':
            self.canvas.scaleWorldWindow(1/(1.1))
        if a.text() == 'zoomOut':
            self.canvas.scaleWorldWindow(1.1)
        if a.text() == 'reset':
            self.canvas.reset()
