import numpy
from datetime import datetime
from math import floor, ceil

from numpy.lib.function_base import select

from he.hecontroller import HeController
from he.hemodel import HeModel
from geometry.segments.line import Line
from geometry.point import Point
from compgeom.tesselation import Tesselation
from compgeom.compgeom import CompGeom

from PyQt5 import QtOpenGL, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from OpenGL.GL import *
from math import *

DRAW_STATE = 1
SELECT_STATE = 2


class MyCanvas(QtOpenGL.QGLWidget):

    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_model = None
        self.m_w = 0  # width: GL canvas horizontal size
        self.m_h = 0  # height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPoint(0.0, 0.0)
        self.m_pt1 = QtCore.QPoint(0.0, 0.0)
        self.m_hmodel = HeModel()
        self.m_controller = HeController(self.m_hmodel)
        self.points_inside_grid = []
        self.state = DRAW_STATE
        self.temperaturas = {}
        self.t_inf = 0

    def initializeGL(self):
        # glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        # enable smooth line display
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)

    def resizeGL(self, _width, _height):
        # store GL canvas sizes in object properties
        self.m_w = _width
        self.m_h = _height
        # Setup world space window limits based on model bounding box
        if (self.m_model == None) or (self.m_model.isEmpty()):
            self.scaleWorldWindow(1.0)
        else:
            self.m_L, self.m_R, self.m_B, self.m_T = self.m_model.getBoundBox()
            self.scaleWorldWindow(1.1)
        # setup the viewport to canvas dimensions
        glViewport(0, 0, self.m_w, self.m_h)
        # reset the coordinate system
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # establish the clipping volume by setting up an
        # orthographic projection
        # glOrtho(0.0, self.m_w, 0.0, self.m_h, -1.0, 1.0)
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        # setup display in model coordinates
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        # clear the buffer with the current clear color
        glClear(GL_COLOR_BUFFER_BIT)
        # draw a triangle with RGB color at the 3 vertices
        # interpolating smoothly the color in the interior
        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        # Display model polygon RGB color at its vertices
        # interpolating smoothly the color in the interior
        # glShadeModel(GL_SMOOTH)
        if self.state == DRAW_STATE:
            pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
            pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(pt0_U.x(), pt0_U.y())
            glVertex2f(pt1_U.x(), pt1_U.y())
            glEnd()
        if not((self.m_model == None) and (self.m_model.isEmpty())):
            verts = self.m_model.getVerts()
            glColor3f(0.0, 1.0, 0.0)  # green
            glBegin(GL_TRIANGLES)
            for vtx in verts:
                glVertex2f(vtx.getX(), vtx.getY())
            glEnd()
            curves = self.m_model.getCurves()
            glColor3f(0.0, 0.0, 1.0)  # blue
            glBegin(GL_LINES)
            for curv in curves:
                glVertex2f(curv.getP1().getX(), curv.getP1().getY())
                glVertex2f(curv.getP2().getX(), curv.getP2().getY())
            glEnd()
        glEndList()

        if not(self.m_hmodel.isEmpty()):
            patches = self.m_hmodel.getPatches()
            for pat in patches:
                pts = pat.getPoints()
                triangs = Tesselation.tessellate(pts)
                for j in range(0, len(triangs)):
                    glColor3f(0.3, 0.8, .8)
                    glBegin(GL_TRIANGLES)
                    glVertex2d(pts[triangs[j][0]].getX(),
                               pts[triangs[j][0]].getY())
                    glVertex2d(pts[triangs[j][1]].getX(),
                               pts[triangs[j][1]].getY())
                    glVertex2d(pts[triangs[j][2]].getX(),
                               pts[triangs[j][2]].getY())
                    glEnd()
                segments = self.m_hmodel.getSegments()
                for curv in segments:
                    ptc = curv.getPointsToDraw()
                    glColor3f(0.0, 1.0, 1.0)
                    glBegin(GL_LINES)
                    for curv in curves:
                        glVertex2f(ptc[0].getX(), ptc[0].getY())
                        glVertex2f(ptc[1].getX(), ptc[1].getY())
                    glEnd()

        glPointSize(5)
        for id, point in enumerate(self.points_inside_grid):
            if id in self.temperaturas.keys():
                glColor3f(1.0, 0.0, 0.0)  # red
            else:
                glColor3f(0.0, 1.0, 0.0)  # green
            glBegin(GL_LINE_LOOP)
            for angulo in range(0, 360, 2):
                radiano = (angulo * pi) / 180

                glVertex2f(point.getX() + self.step_x/4 * cos(radiano),
                           point.getY() + self.step_x/4 * sin(radiano))
            glEnd()

            glBegin(GL_POINTS)
            glVertex2f(point.getX(), point.getY())
            glEnd()

        if self.state == SELECT_STATE:
            pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
            pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(pt0_U.x(), pt0_U.y())
            glVertex2f(pt1_U.x(), pt0_U.y())
            glVertex2f(pt1_U.x(), pt1_U.y())
            glVertex2f(pt0_U.x(), pt1_U.y())
            glVertex2f(pt0_U.x(), pt0_U.y())
            glEnd()

    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x, y)

    def convertCoordsToUniverse(self, coordX, coordY):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = coordX * dX / self.m_w
        mY = (self.m_h - coordY) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return x, y

    def mousePressEvent(self, event):
        self.m_buttonPressed = True
        self.m_pt0 = event.pos() * 2
        # self.m_pt0 = event.pos()
        self.m_pt1 = self.m_pt0

    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            # self.m_pt1 = event.pos()
            self.m_pt1 = event.pos() * 2
            self.update()

    def mouseReleaseEvent(self, event):
        if self.state == DRAW_STATE:
            pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
            pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
            if pt0_U.x() == pt1_U.x() and pt0_U.y() == pt1_U.y():
                # Missclick, não adicionar reta sem tamanho
                return
            self.m_model.setCurve(pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y())
            p0 = Point(pt0_U.x(), pt0_U.y())
            p1 = Point(pt1_U.x(), pt1_U.y())
            segment = Line(p0, p1)
            self.m_controller.insertSegment(segment, 0.01)
            # self.m_model.setCurve(self.m_pt0.x(),self.m_pt0.y(),self.m_pt1.x(),self.m_pt1.y())
            self.m_buttonPressed = False
            self.m_pt0.setX(0.0)
            self.m_pt0.setY(0.0)
            self.m_pt1.setX(0.0)
            self.m_pt1.setY(0.0)
            self.update()
        if self.state == SELECT_STATE:
            self.chooseTemp()

    def setModel(self, _model):
        self.m_model = _model

    def fitWorldToViewport(self):
        if self.m_model == None:
            return
        self.m_L, self.m_R, self.m_B, self.m_T = self.m_model.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()

    def scaleWorldWindow(self, _scaleFac):
        # Compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w
        # Get current window center.
        # /*** COMPLETE HERE - GLCANVAS: 01 ***/
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0
        # /*** COMPLETE HERE - GLCANVAS: 01 ***/
        # Set new window sizes based on scaling factor.
        # /*** COMPLETE HERE - GLCANVAS: 02 ***/
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac
        # /*** COMPLETE HERE - GLCANVAS: 02 ***/
        # Adjust window to keep the same aspect ratio of the viewport.
        # /*** COMPLETE HERE - GLCANVAS: 03 ***/
        if sizey > (vpr*sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr
        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)
        # /*** COMPLETE HERE - GLCANVAS: 03 ***/
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        self.update()

    def panWorldWindow(self, _panFacX, _panFacY):
        # Compute pan distances in horizontal and vertical directions.
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        # Shift current window.
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        self.update()

    def reset(self):
        self.m_model.deleteCurves()
        self.m_hmodel.clearAll()
        self.points_inside_grid = []
        self.update()

        self.paintGL()

    def debug(self):
        print(self.m_model)
        bound_box = self.m_hmodel.getBoundBox()
        print("BOUNDING BOX:")
        print(bound_box)
        print("🎁")

    def print_convex_hull(self):
        print("-"*100)
        print(datetime.now().time())
        if not(self.m_hmodel.isEmpty()):
            patches = self.m_hmodel.getPatches()
            if not patches:
                print("Model doesn't have convex hulls")
            for num, pat in enumerate(patches):
                pts = pat.getPoints()
                print("-"*50)
                print(f'Fecho {num}')
                print(pts)
        else:
            print("Model is empty")

    def generate_grid(self, qtd_horizontal=100, qtd_vertical=100):
        bound_box = self.m_hmodel.getBoundBox()
        self.step_x = abs(ceil(bound_box[1])-bound_box[0])/qtd_horizontal
        self.step_y = abs(ceil(bound_box[3])-bound_box[2])/qtd_vertical
        if bound_box[0] != 0:
            minX = (floor(bound_box[0]/self.step_y) + 1)*self.step_y
        else:
            minX = self.step_x
        minY = (floor(bound_box[2]/self.step_y) + 1)*self.step_y
        self.points_inside_grid = []
        polygons = self.m_hmodel.getPatches()
        self.matrizpontos = []
        indice = 0
        for y in numpy.arange(ceil(bound_box[3]), minY,  -self.step_y):
            linhamatriz = []
            for x in numpy.arange(minX, ceil(bound_box[1]), self.step_x):
                p0 = Point(x, y)
                for polygon in polygons:
                    pts = polygon.getPoints()
                    if CompGeom.isPointInPolygon(pts, p0):
                        self.points_inside_grid.append(p0)
                        indice += 1
                        linhamatriz.append(indice)
                    else:
                        linhamatriz.append(0)
            self.matrizpontos.append(linhamatriz)
        self.update()
        self.temperaturas = {}

    def draw_bound_box(self):
        bound_box = self.m_hmodel.getBoundBox()
        p0 = Point(bound_box[0], bound_box[2])
        p1 = Point(bound_box[1], bound_box[2])
        segment = Line(p0, p1)
        self.m_controller.insertSegment(segment, 0.01)

        # p0 = Point(bound_box[0], bound_box[3])
        # p1 = Point(bound_box[1], bound_box[3])
        # segment = Line(p0, p1)
        # self.m_controller.insertSegment(segment, 0.01)

        p0 = Point(bound_box[0], bound_box[2])
        p1 = Point(bound_box[0], bound_box[3])
        segment = Line(p0, p1)
        self.m_controller.insertSegment(segment, 0.01)

        # p0 = Point(bound_box[1], bound_box[2])
        # p1 = Point(bound_box[1], bound_box[3])
        # segment = Line(p0, p1)
        # self.m_controller.insertSegment(segment, 0.01)
        self.update()

    def getPointsInsideGrid(self):
        return self.points_inside_grid

    def getMatriz(self):
        return self.matrizpontos

    def createConnect(self):
        connect = []
        for linha_id in range(0, len(self.matrizpontos)):
            for coluna_id in range(len(self.matrizpontos[linha_id])):
                if not self.matrizpontos[linha_id][coluna_id]:
                    continue
                if linha_id != 0:
                    cima = self.matrizpontos[linha_id-1][coluna_id]
                else:
                    cima = 0
                if coluna_id != 0:
                    esq = self.matrizpontos[linha_id][coluna_id - 1]
                else:
                    esq = 0
                if linha_id != len(self.matrizpontos)-1:
                    baixo = self.matrizpontos[linha_id+1][coluna_id]
                else:
                    baixo = 0
                if coluna_id != len(self.matrizpontos[linha_id])-1:
                    dir = self.matrizpontos[linha_id][coluna_id+1]
                else:
                    dir = 0

                connect.append([
                    dir,
                    esq,
                    baixo,
                    cima
                ])
        return connect

    def setSelectState(self):
        self.state = SELECT_STATE

    def setDrawState(self):
        self.state = DRAW_STATE

    def getTemperaturas(self):
        temperaturas = []
        for index, point in enumerate(self.points_inside_grid):
            if index in self.temperaturas.keys():
                temperaturas.append([1, self.temperaturas[index]])
            else:
                temperaturas.append([0, 0])
        return temperaturas

    def setTemperaturas(self, temperatura):
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        inside = [Point(pt0_U.x(), pt0_U.y()),
                  Point(pt1_U.x(), pt0_U.y()),
                  Point(pt1_U.x(), pt1_U.y()),
                  Point(pt0_U.x(), pt1_U.y())]
        for indice, point in enumerate(self.points_inside_grid):
            if CompGeom.isPointInPolygon(inside, point):
                self.temperaturas[indice] = temperatura

    def chooseTemp(self):
        temp, ok = QInputDialog.getText(self, 'Input Horizontal',
                                        'Temperatura dos pontos selecionados:')
        if not ok:
            return
        try:
            temp = float(temp)
            self.setTemperaturas(temp)
        except:
            QMessageBox.about(self, 'ERRO',
                              "Erro ao transformar temperatura em ponto flutuante.")
            return

    def getSteps(self):
        return {
            'step_x':  self.step_x,
            'step_y': self.step_y
        }
