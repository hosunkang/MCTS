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
        self.pix = QPixmap(self.draw_label.size())
        self.pts = None
        self.start_pts = [[(50,225),(50,275)],
                          [(80,230),(20,230),(80,270),(20,270)]]
        self.goal_area = (900,200,100,100)

        # Initial values setting
        self.value_mcts = self.slider_mcts.value()
        self.value_mcts_2 = self.slider_mcts_2.value()
        self.robot_type_idx = self.robot_type.currentIndex()
        self.mcts_type_idx = self.mcts_type.currentIndex()

        # PyQT functions
        self.load_pcd.triggered.connect(self.pcd_file_opener)
        self.cleaner.clicked.connect(self.cleaner_clicked)
        self.bt_mcts.clicked.connect(self.bt_mcts_clicked)
        self.slider_mcts.valueChanged.connect(self.mcts_changed)
        self.slider_mcts_2.valueChanged.connect(self.mcts_2_changed)
        self.robot_type.currentIndexChanged.connect(self.robot_type_function)
        self.mcts_type.currentIndexChanged.connect(self.mcts_type_function)

    def pcd_file_opener(self):
        filename = QFileDialog.getOpenFileName(self, "Open PCD file", './', "*.pcd")
        filename = filename[0]
        pcu = pcdutils()
        self.pts = pcu.get_pcd_2d(filename)
        self.pix.fill(Qt.transparent)
        self.draw_pts()

    def mcts_changed(self):
        self.value_mcts = self.slider_mcts.value()
        self.lbl_mcts.setText(str(self.value_mcts))

    def mcts_2_changed(self):
        self.value_mcts_2 = self.slider_mcts_2.value()
        self.lbl_mcts_2.setText(str(self.value_mcts_2))
    
    def robot_type_function(self):
        self.robot_type_idx = self.robot_type.currentIndex()
        self.pix.fill(Qt.transparent)
        self.draw_pts()
    
    def mcts_type_function(self):
        self.mcts_type_idx = self.mcts_type.currentIndex()

    def draw_pts(self):
        qp = QPainter(self.pix)
        qp.setBrush(Qt.green)
        for w,h in self.start_pts[self.robot_type_idx]:    
            qp.drawRect(w-5, h-5, 10, 10)
        if self.pts is not None:
            qp.setBrush(Qt.SolidPattern)
            for x,y in self.pts:
                qp.drawRect(x-2, y-2, 4, 4)
        qp.setBrush(Qt.transparent)
        qp.setPen(QPen(Qt.red, 3))
        qp.drawRect(self.goal_area[0],self.goal_area[1],self.goal_area[2],self.goal_area[3])
        self.draw_label.setPixmap(self.pix)
        qp.end()

    def drawND(self, snd, end):
        qp = QPainter(self.pix)
        color = QColor(random.randrange(255),random.randrange(255),random.randrange(255))
        qp.setPen(QPen(color,  5))
        qp.drawPoint(end[0],end[1])
        qp.setPen(QPen(color,  2))
        qp.drawLine(snd[0], snd[1], end[0], end[1])
        self.draw_label.setPixmap(self.pix)
        qp.end()
    
    def cleaner_clicked(self):
        self.draw_pts()
    
    def bt_mcts_clicked(self):
        mcts = standard_MCTS(self.value_mcts, self.value_mcts_2)  
        NDs = mcts.mcts(self.start_pts[self.robot_type_idx], self.goal_area, self.pts)
        # self.drawND(temp_start_pts, NDs)

    # def bt_mcts_clicked(self):
    #     mcts = momentum_MCTS(self.value_mcts, self.value_mcts_2)  
    #     temp_start_pt = self.start_pts[self.robot_type_idx]
    #     start = time.time()
    #     while(1):
    #         endND = mcts.mcts(temp_start_pt, self.goal_area, self.planars[:])
    #         if endND == None:
    #             self.drawND(temp_start_pt, temp_start_pt)
    #             result = "Fail"
    #             break
    #         elif endND.pos == self.goal_area:
    #             self.drawND(temp_start_pt, endND.pos)
    #             result = "Good"
    #             break
    #         else:
    #             self.drawND(temp_start_pt, endND.pos)
    #             temp_start_pt = endND.pos
    #     ts = time.time()-start
    #     item = QListWidgetItem("T:{:0.4f} P:{:3d} Iter:{:4d} R:{:3d} = {}".format(ts,
    #                                                                               len(self.planars)-1,
    #                                                                               self.value_mcts,
    #                                                                               self.value_mcts_2,
    #                                                                               result))
    #     self.listWidget.addItem(item)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyWindow()
   ex.show()
   sys.exit(app.exec_())