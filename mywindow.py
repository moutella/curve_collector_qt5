import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from mycanvas import *
from mymodel import *
from geometry.point import PointJSONEncoder
import os


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100, 100, 1024, 860)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.qtd_horizontal = 10
        self.qtd_vertical = 10
        self.setCentralWidget(self.canvas)
        # create a model object and pass it to canvas object
        self.model = MyModel()
        self.canvas.setModel(self.model)
        # create a Toolbar
        tb = self.addToolBar("File")
        fit = QAction(QIcon("icons/fit.jpg"), "fit", self)
        tb.addAction(fit)

        button = QAction("JSON", self)
        tb.addAction(button)
        button = QAction("DEFINIR_GRID", self)
        tb.addAction(button)

        self.qtd_horizontal_visor = QLabel(f"Hor.: {self.qtd_horizontal}")
        tb.addWidget(self.qtd_horizontal_visor)

        self.qtd_vertical_visor = QLabel(f"Ver.: {self.qtd_vertical}")
        tb.addWidget(self.qtd_vertical_visor)

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

        reset = QAction(QIcon("icons/reset.png"), "reset", self)
        tb.addAction(reset)

        generate_grid = QAction(QIcon("icons/grid.jpg"), "grid", self)
        tb.addAction(generate_grid)

        set_temp = QAction(QIcon("icons/temp.png"), "temp", self)
        tb.addAction(set_temp)

        edit_project = QAction(QIcon("icons/edit.png"), "draw", self)
        tb.addAction(edit_project)

        # debug = QAction(QIcon("icons/grid.jpg"), "debug", self)
        # tb.addAction(debug)

        # print_hull = QAction(QIcon("icons/fit.jpg"), "print_hull", self)
        # tb.addAction(print_hull)
        # draw_bound_box = QAction(
        #     QIcon("icons/fit.jpg"), "draw_bound_box", self)
        # tb.addAction(draw_bound_box)

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
            self.canvas.generate_grid(self.qtd_horizontal, self.qtd_vertical)
        if action.text() == 'debug':
            self.canvas.debug()

        if action.text() == 'print_hull':
            self.canvas.print_convex_hull()
        if action.text() == 'draw_bound_box':
            self.canvas.draw_bound_box()

        if action.text() == 'temp':
            self.canvas.setSelectState()
        if action.text() == 'draw':
            self.canvas.setDrawState()

        if action.text() == 'JSON':
            points = self.canvas.getPointsInsideGrid()
            connect = self.canvas.createConnect()
            temperaturas = self.canvas.getTemperaturas()
            distancias = self.canvas.getSteps()
            saida = {
                # 'points': points,
                'connect': connect,
                'temperaturas': temperaturas,
                'step': distancias
            }
            # points = [repr(point) for point in points]
            with open('problema.json', 'w', encoding='utf-8') as f:
                json.dump(saida, f, indent=4, cls=PointJSONEncoder)

        if action.text() == 'DEFINIR_GRID':
            self.showDialog()

    def showDialog(self):
        pts_horizontais, ok = QInputDialog.getText(self, 'Input Horizontal',
                                                   'Quantidades de pontos Horizontais:')
        if not ok:
            return
        try:
            self.qtd_horizontal = int(pts_horizontais)
        except:
            QMessageBox.about(self, 'ERRO',
                              "Erro ao transformar quantidade horizontal em inteiro")
            return
        self.qtd_horizontal_visor.setText((f"Hor.: {self.qtd_horizontal}"))

        pts_verticais, ok = QInputDialog.getText(self, 'Input Vertical',
                                                 'Quantidades de pontos Verticais:')
        if not ok:
            return
        try:
            self.qtd_vertical = int(pts_verticais)
        except:
            QMessageBox.about(self, 'ERRO',
                              "Erro ao transformar quantidade vertical em inteiro")
            return
        self.qtd_vertical_visor.setText((f"Ver.: {self.qtd_vertical}"))
