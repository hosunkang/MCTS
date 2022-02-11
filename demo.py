import sys, random, math, time
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

        self.bt_draw_planar.clicked.connect(self.bt_draw_clicked)
        self.bt_mcts.clicked.connect(self.bt_mcts_clicked)
        self.slider_planar.valueChanged.connect(self.planar_changed)
        self.slider_mcts.valueChanged.connect(self.mcts_changed)
        self.slider_mcts_2.valueChanged.connect(self.mcts_2_changed)

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
        self.startpt = (10,250)
        self.goalpt = (1000,250)
        self.planars = []
        self.pix = QPixmap(self.draw_label.size())
        self.pix.fill(Qt.transparent)
        qp = QPainter(self.pix)

        # Start
        qp.setBrush(Qt.green)
        qp.drawRect(self.startpt[0]-10, self.startpt[1]-10, 20, 20)
        # Goal
        qp.setBrush(Qt.red)
        qp.drawRect(self.goalpt[0]-10, self.goalpt[1]-10, 20, 20)

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
        mcts = FunctionMCTS(self.value_mcts, self.value_mcts_2)
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

########Node class#############
class node:
    def __init__(self, pos=[0,0], vis=0, val=0, utc=0, paND=None):
        self.pos = pos
        self.vis = vis
        self.val = val
        self.utc = utc
        self.parentND = paND
        self.childNDs = []
        self.candiNDs = []

#########MCTS Class############
class FunctionMCTS:
    def __init__(self, value_mcts, value_mcts_2):
        super().__init__()
        self.iterations = value_mcts
        self.limit_l = value_mcts_2

    def mcts(self, spt, gpt, pts):
        root_nd = node(spt, 0, 0, None, None)
        for i in range(self.iterations):
            se_node = self.selection(root_nd, pts)
            if se_node == None:
                return None
            ex_node = self.expansion(se_node)
            result = self.simulation(ex_node.pos, pts[:], gpt)
            self.backprop(result, ex_node)
        return self.finalSelect(root_nd)

    def find_candidate(self, nd, pts):
        for i in range(len(pts)):
            x = pts[i][0] - nd.pos[0]
            y = pts[i][1] - nd.pos[1]
            l = math.sqrt((x*x)+(y*y))
            if l < self.limit_l and x > 0:
                nd.candiNDs.append(node(pts[i], 0, 0, 0, nd))

    def selection(self, cnd, pts):
        self.find_candidate(cnd, pts)
        if len(cnd.candiNDs) + len(cnd.childNDs) == 0:
            snd = None
        elif len(cnd.candiNDs) != 0:
            snd = cnd
        else:
            max = -100
            max_nd = node()
            for i in range(len(cnd.childNDs)):
                if cnd.childNDs[i].uct > max:
                    max_nd = cnd.childNDs[i]
                    max = max_nd.uct
            snd = self.selection(max_nd, pts)
        return snd

    def expansion(self, snd):
        end = snd.candiNDs[random.randrange(len(snd.candiNDs))]
        snd.childNDs.append(end)
        snd.candiNDs.remove(end)
        return end

    def get_dist(self, pt1, pt2):
        x = pt2[0] - pt1[0]
        y = pt2[1] - pt1[1]
        d = math.sqrt((x*x)+(y*y))
        return x,d

    def simulation(self, endp, pts, gpt):
        while(1):
            if self.get_dist(endp,gpt)[1] < self.limit_l:
                return 1
            canpts = []
            temp_pts = pts[:]
            for i in range(len(temp_pts)):
                x,l = self.get_dist(endp, temp_pts[i])
                if x < 0 or endp==temp_pts[i]:
                    pts.remove(temp_pts[i])
                else:
                    if l < self.limit_l:
                        canpts.append(temp_pts[i])
            if len(canpts) == 0:
                return 0
            else:
                endp = canpts[random.randrange(len(canpts))]

    def uctFunc(self, w, n, t):
        return (w/n)+math.sqrt(2*math.log(t)/n)

    def backprop(self, result, nd):
        nd.vis += 1
        if nd.parentND is not None:
            if result == 1:
                nd.val += 1
            self.backprop(result, nd.parentND)
            nd.uct = self.uctFunc(nd.val, nd.vis, nd.parentND.vis)

    def finalSelect(self, root_nd):
        max = -100
        for i in range(len(root_nd.childNDs)):
            exploitation = root_nd.childNDs[i].val / root_nd.childNDs[i].vis
            if exploitation > max:
                max_nd = root_nd.childNDs[i]
                max = exploitation
        if max == -100:
            return None
        else:
            return max_nd


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyWindow()
   ex.show()
   sys.exit(app.exec_())