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
        self.bt_draw_planar.clicked.connect(self.bt_draw_clicked)
        self.bt_mcts.clicked.connect(self.bt_mcts_clicked)

    def bt_draw_clicked(self, event):
        print("Click Draw planar button")
        self.pix = QPixmap(self.draw_label.size()) #size(1021,501)
        self.pix.fill(Qt.transparent)
        qp = QPainter(self.pix)

        # Start
        qp.setBrush(Qt.green)
        qp.drawRect(0, 250, 20, 20)
        # Goal
        qp.setBrush(Qt.red)
        qp.drawRect(1000, 250, 20, 20)

        qp.setBrush(Qt.SolidPattern)
        for i in range(100):
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