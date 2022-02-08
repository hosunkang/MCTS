from email.charset import QP
import sys, random
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

form_class = uic.loadUiType("ui_treesearch.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.value_planar = self.slider_planar.value()
        self.mcts_planar = self.slider_mcts.value()

        self.bt_draw_planar.clicked.connect(self.bt_draw_clicked)
        self.bt_mcts.clicked.connect(self.bt_mcts_clicked)
        self.slider_planar.valueChanged.connect(self.planar_changed)
        self.slider_mcts.valueChanged.connect(self.mcts_changed)

    def planar_changed(self):
        self.value_planar = self.slider_planar.value()
        self.lbl_planar.setText(str(self.value_planar))

    def mcts_changed(self):
        self.value_mcts = self.slider_mcts.value()
        self.lbl_mcts.setText(str(self.value_mcts))

    def bt_draw_clicked(self):
        print("Click Draw planar button")
        self.pix = QPixmap(self.draw_label.size())
        self.pix.fill(Qt.transparent)
        qp = QPainter(self.pix)

        # Start
        qp.setBrush(Qt.green)
        qp.drawRect(0, 240, 20, 20)
        # Goal
        qp.setBrush(Qt.red)
        qp.drawRect(990, 250, 20, 20)

        qp.setBrush(Qt.SolidPattern)
        for i in range(self.value_planar):
            w = random.randrange(0, 1000)
            h = random.randrange(0, 450)
            qp.drawRect(w, h, 20, 20)
        self.draw_label.setPixmap(self.pix)

    def bt_mcts_clicked(self):
        print("Click MCTS button")

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyWindow()
   ex.show()
   sys.exit(app.exec_())