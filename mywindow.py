from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
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
        pan_right = QAction(QIcon("icons/panright.jpg"), "pan_right", self)
        tb.addAction(pan_right)
        pan_left = QAction(QIcon("icons/panleft.jpg"), "pan_left", self)
        tb.addAction(pan_left)
        pan_up = QAction(QIcon("icons/panup.jpg"), "pan_up", self)
        tb.addAction(pan_up)
        pan_down = QAction(QIcon("icons/pandown.jpg"), "pan_down", self)
        tb.addAction(pan_down)

        # Zoom
        zoom_in = QAction(QIcon("icons/zoomin.jpg"), "zoom_in", self)
        tb.addAction(zoom_in)
        zoom_out = QAction(QIcon("icons/zoomout.jpg"), "zoom_out", self)
        tb.addAction(zoom_out)

        reset = QAction(QIcon("icons/delete.jpg"), "reset", self)
        tb.addAction(reset)

        generate_grid = QAction(QIcon("icons/grid.jpg"), "grid", self)
        tb.addAction(generate_grid)

        tb.actionTriggered[QAction].connect(self.tbpressed)
#        tb2 = self.addToolBar("Draw")
#        line = QAction(QIcon("icons/fit.jpg"),"line",self)
#        tb2.addAction(line)

    def tbpressed(self, action):
        if action.text() == "fit":
            self.canvas.fitWorldToViewport()
        if action.text() == 'pan_right':
            self.canvas.panWorldWindow(-0.2, 0)
        if action.text() == 'pan_left':
            self.canvas.panWorldWindow(0.2, 0)
        if action.text() == 'pan_up':
            self.canvas.panWorldWindow(0, -0.2)
        if action.text() == 'pan_down':
            self.canvas.panWorldWindow(0, 0.2)
        if action.text() == 'zoom_in':
            self.canvas.scaleWorldWindow(1/(1.1))
        if action.text() == 'zoom_out':
            self.canvas.scaleWorldWindow(1.1)
        if action.text() == 'reset':
            self.canvas.reset()
        if action.text() == 'grid':
            self.canvas.generateGrid()
