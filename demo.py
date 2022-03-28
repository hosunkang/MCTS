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
        self.start_pts = [[(50,200),(50,300)],
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

    def drawPT(self, pos):
        qp = QPainter(self.pix)
        color = QColor(random.randrange(255),random.randrange(255),random.randrange(255))
        qp.setPen(QPen(Qt.red,  5))
        qp.drawPoint(pos[0],pos[1])
        self.draw_label.setPixmap(self.pix)
        qp.end()

    def drawRobotND(self,nd):
        qp = QPainter(self.pix)
        color = QColor(random.randrange(125,255),random.randrange(125,255),random.randrange(125,255))
        qp.setPen(QPen(Qt.blue,  2))
        for leg in nd.childNDs:
            qp.drawLine(leg.pos[0], leg.pos[1], nd.pos[0], nd.pos[1])
        qp.setPen(QPen(Qt.blue,  5))
        for leg in nd.childNDs:
            qp.drawPoint(leg.pos[0],leg.pos[1])
        qp.setPen(QPen(Qt.red,  5))
        qp.drawPoint(nd.pos[0],nd.pos[1])
        self.draw_label.setPixmap(self.pix)
        qp.end()
        QApplication.processEvents()

    def drawRobotPT(self, pts):
        qp = QPainter(self.pix)
        color = QColor(random.randrange(125,255),random.randrange(125,255),random.randrange(125,255))
        qp.setPen(QPen(Qt.blue,  2))
        qp.drawLine(pts[0][0], pts[0][1], pts[1][0], pts[1][1])
        qp.setPen(QPen(Qt.blue,  5))
        for leg in pts:
            qp.drawPoint(leg[0],leg[1])
        self.draw_label.setPixmap(self.pix)
        qp.end()
        QApplication.processEvents()
    
    def cleaner_clicked(self):
        self.pix.fill(Qt.transparent)
        self.draw_pts()
    
    def addNDinfo(self, top, nd):
        QTreeWidgetItem(top, ["pos", str(nd.pos)])
        QTreeWidgetItem(top, ["vis", str(nd.vis)])
        QTreeWidgetItem(top, ["val", str(nd.val)])
        QTreeWidgetItem(top, ["UTC", "{:.4f}".format(nd.utc)])

    def bt_mcts_clicked(self):
        self.treeWidget.clear()
        mcts = standard_MCTS(self, self.value_mcts, self.value_mcts_2)  
        start = time.time()
        nds, maxNDs = mcts.mcts(self.start_pts[self.robot_type_idx], self.goal_area, self.pts)
        ts = time.time()-start
        print(ts)

        for idx, (nd, max) in enumerate(zip(nds,maxNDs)):
            topitem = QTreeWidgetItem()
            topitem.setText(0, "#{} step".format(idx+1))
            self.treeWidget.addTopLevelItem(topitem)
            childitem = QTreeWidgetItem(topitem, ["Select Node"])
            self.addNDinfo(childitem, max)
            for cidx, cnd in enumerate(nd.childNDs):
                childitem = QTreeWidgetItem(topitem)
                childitem.setText(0, "#{} child Node".format(cidx+1))
                self.addNDinfo(childitem, cnd)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyWindow()
   ex.show()
   sys.exit(app.exec_())