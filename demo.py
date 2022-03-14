import sys, random, time
from mcts import *
from pcutils import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt

form_class = uic.loadUiType("ui_treesearch.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.clean = QPixmap(self.draw_label.size())

        self.value_planar = self.slider_planar.value()
        self.value_mcts = self.slider_mcts.value()
        self.value_mcts_2 = self.slider_mcts_2.value()

        self.load_pcd.triggered.connect(self.pcd_file_opener)

        self.bt_draw_planar.clicked.connect(self.bt_draw_clicked)
        self.bt_mcts.clicked.connect(self.bt_mcts_clicked)
        self.slider_planar.valueChanged.connect(self.planar_changed)
        self.slider_mcts.valueChanged.connect(self.mcts_changed)
        self.slider_mcts_2.valueChanged.connect(self.mcts_2_changed)

    def pcd_file_opener(self):
        filename = QFileDialog.getOpenFileName(self, "Open PCD file", './')
        filename = filename[0]
        pcu = pcdutils()
        pcu.get_pcd_2d(filename)

    def planar_changed(self):
        self.value_planar = self.slider_planar.value()
        self.lbl_planar.setText(str(self.value_planar))

    def mcts_changed(self):
        self.value_mcts = self.slider_mcts.value()
        self.lbl_mcts.setText(str(self.value_mcts))

    def mcts_2_changed(self):
        self.value_mcts_2 = self.slider_mcts_2.value()
        self.lbl_mcts_2.setText(str(self.value_mcts_2))

    def bt_draw_clicked(self):
        self.information.setText("Click Draw planar button")
        simul_version = self.comboBox_1.currentIndex()
        self.pix = QPixmap(self.draw_label.size())
        self.pix.fill(Qt.transparent)
        qp = QPainter(self.pix)

        self.startpt = (10,250)
        self.goalpt = (1000,250)

        # Start
        qp.setBrush(Qt.green)
        qp.drawRect(self.startpt[0]-10, self.startpt[1]-10, 20, 20)
        # Goal
        qp.setBrush(Qt.red)
        qp.drawRect(self.goalpt[0]-10, self.goalpt[1]-10, 20, 20)

        self.planars = []
        qp.setBrush(Qt.SolidPattern)
        for i in range(self.value_planar):
            w = random.randrange(20, 980)
            h = random.randrange(20, 450)
            qp.drawRect(w, h, 20, 20)
            self.planars.append([w+10, h+10])
        self.planars.append(self.goalpt)
        self.draw_label.setPixmap(self.pix)
        qp.end()

    def drawND(self, snd, end):
        qp = QPainter(self.pix)
        qp.setPen(QPen(self.color,  5))
        qp.drawPoint(end[0],end[1])
        qp.setPen(QPen(self.color,  2))
        qp.drawLine(snd[0], snd[1], end[0], end[1])
        self.draw_label.setPixmap(self.pix)
        qp.end()

    def bt_mcts_clicked(self):
        self.information.setText("Click MCTS button")
        self.draw_label.setPixmap(self.clean)
        mcts = momentum_MCTS(self.value_mcts, self.value_mcts_2)
        temp_start_pt = self.startpt
        self.color = QColor(random.randrange(255),random.randrange(255),random.randrange(255))
        start = time.time()
        while(1):
            endND = mcts.mcts(temp_start_pt, self.goalpt, self.planars[:])
            if endND == None:
                self.drawND(temp_start_pt, temp_start_pt)
                self.information.setText("Ooops!!!! I can't get there!")
                result = "Fail"
                break
            elif endND.pos == self.goalpt:
                self.drawND(temp_start_pt, endND.pos)
                self.information.setText("Finally i came here!!!")
                result = "Good"
                break
            else:
                self.drawND(temp_start_pt, endND.pos)
                temp_start_pt = endND.pos
        ts = time.time()-start
        self.label_time.setText("Time : {:0.4f}".format(ts))
        item = QListWidgetItem("T:{:0.4f} P:{:3d} Iter:{:4d} R:{:3d} = {}".format(ts,
                                                                                  len(self.planars)-1,
                                                                                  self.value_mcts,
                                                                                  self.value_mcts_2,
                                                                                  result))
        self.listWidget.addItem(item)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyWindow()
   ex.show()
   sys.exit(app.exec_())