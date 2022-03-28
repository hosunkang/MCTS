from demo import MyWindow
import random, math
import time

########Node class#############
# candiNDs = The nodes can be selected in policy
# childNDs = Already Expanded nodes, so, it has UTC value
class node:
    def __init__(self, pos=[0,0], vis=0, val=0, utc=0.0, paND=None):
        self.pos = pos
        self.vis = vis
        self.val = val
        self.utc = utc
        self.parentND = paND
        self.childNDs = []
        self.candiNDs = []

#########MCTS Class############
class standard_MCTS:
    def __init__(self, window, value_mcts, value_mcts_2):
        super().__init__()
        self.iterations = value_mcts
        self.stepCount = value_mcts_2
        self.Min_robotWidth, self.Max_robotWidth = 50, 150
        self.window = window
        self.stepLeg = 0

    def get_dist(self, pt1, pt2):
        x = pt2[0] - pt1[0]
        y = pt2[1] - pt1[1]
        d = math.sqrt((x*x)+(y*y))
        return x,y,d
    
    def get_robotCenter(self, legs):
        x_sum = 0
        y_sum = 0
        for pos in legs:
            x_sum += pos[0]
            y_sum += pos[1]
        else:
            center = [x_sum/len(legs),y_sum/len(legs)]
        return center

    def get_rootND(self, spts):
        ## Root node == first step leg (0 -> max)
        nd = node(spts[self.stepLeg]) 
        for idx,pos in enumerate(spts):
            if idx != self.stepLeg:
                nd.childNDs.append(node(pos=pos, vis=1, paND=nd))
        return nd

    def get_candiND(self, nd, pts):
        for pt in pts:
            x, y, width = self.get_dist(nd.pos, pt)
            _, y_1, _ = self.get_dist(nd.parentND.pos, pt)
            _, y_2, _ = self.get_dist(nd.parentND.pos, nd.pos)

            if self.Min_robotWidth < width < self.Max_robotWidth and x > 10 and abs(y) > self.Min_robotWidth:
                if abs(y_1) < abs(y_2):
                    nd.candiNDs.append(node(pos=pt, paND=nd))
        return nd

    def check_goal(self, pt, goal):
        x,y = pt
        x_min, x_max = goal[0], goal[0]+goal[2]
        y_min, y_max = goal[1], goal[1]+goal[3]
        if x_min<x<x_max  and y_min<y<y_max:
            return 1    
        else:
            return 0
    
    def findSimulPts(self, stop, move, pts):
        candiPTs = []
        for pt in pts:
            x, y, width = self.get_dist(stop, pt)
            _, y_1, _ = self.get_dist(move, pt)
            _, y_2, _ = self.get_dist(move, stop)

            if self.Min_robotWidth < width < self.Max_robotWidth and x > 10 and abs(y) > self.Min_robotWidth:
                if abs(y_1) < abs(y_2):
                    candiPTs.append(pt)
        return candiPTs

    # UTC value function
    # w: N. of win , n: N. of visit in child node, t: N. of visit in parent node
    def utcFunc(self, nd):
        w, n, t = nd.val, nd.vis, nd.parentND.vis
        if n != 0:
            return float((w/n)+math.sqrt(2*math.log(t)/n))
        else:
            return 0

    def printND(self, nd):
        print(nd.pos, nd.vis, nd.val, nd.utc, len(nd.childNDs))

    # selection -> expansion -> simulation -> backpropagation -> final selection
    def mcts(self, spts, garea, pts):
        finalNDs = []
        maxNDs = []
        rootND = self.get_rootND(spts)
        for j in range(self.stepCount):
            start = time.time()
            for i in range(self.iterations):
                seleND = self.selection(rootND, pts)
                expaND = self.expansion(seleND)
                result = self.simulation(expaND, pts, garea)
                self.backprop(result, expaND)
            else:
                spts, maxND = self.finalSelect(rootND)
                ts = time.time()-start
                print("#{} Iteration is done : {} s".format(j+1, ts))
    
                finalNDs.append(rootND.childNDs[0])
                maxNDs.append(maxND)

                rootND = self.get_rootND(spts)
                self.window.drawRobotND(rootND)

                ## Check goal
                legs = [rootND.pos]
                for nd in rootND.childNDs:
                    legs.append(nd.pos)
                if self.check_goal(self.get_robotCenter(legs),garea) == 1:
                    break
        
        return finalNDs, maxNDs

    def selection(self, nd, pts):
        if len(nd.candiNDs) == 0 and len(nd.childNDs) == 0:
            nd = self.get_candiND(nd, pts)

        if len(nd.candiNDs) == 0 and len(nd.childNDs) != 0:
            max = -100
            temp_nd = node()
            for i in range(len(nd.childNDs)):
                if nd.childNDs[i].utc > max:
                    temp_nd = nd.childNDs[i]
                    max = nd.childNDs[i].utc
            snd = self.selection(temp_nd, pts)
        else:
            snd = nd
        return snd
    
    def expansion(self, nd):
        if len(nd.candiNDs) != 0:
            end = nd.candiNDs[random.randrange(len(nd.candiNDs))]
            nd.childNDs.append(end)
            nd.candiNDs.remove(end)
            return end
        else:
            return nd

    def simulation(self, end, pts, goal):
        stopLeg = end.pos
        moveLeg = end.parentND.pos
        robotCenter = self.get_robotCenter([stopLeg, moveLeg])
        
        while(1):
            robotCenter = self.get_robotCenter([stopLeg, moveLeg])
            if self.check_goal(robotCenter, goal) == 1:
                return 1
            elif robotCenter[0] > 950:
                return 0
            else:
                candiPTs = self.findSimulPts(stopLeg, moveLeg, pts)
                if len(candiPTs) == 0: ## There are no possible move points
                    ## Change the move leg
                    temp = stopLeg
                    stopLeg = moveLeg
                    moveLeg = temp
                    candiPTs = self.findSimulPts(stopLeg, moveLeg, pts)
                    if len(candiPTs) == 0:
                        return 0
                moveLeg = stopLeg
                stopLeg = candiPTs[random.randrange(len(candiPTs))]

    
    def backprop(self, result, nd):
        nd.vis += 1
        if result == 1:
            nd.val += 1
        if nd.parentND is not None:
            self.backprop(result, nd.parentND)
            for child in nd.parentND.childNDs:
                child.utc = self.utcFunc(child)
    
    def finalSelect(self, rnd):
        max = -100
        maxND = node()
        for nd in rnd.childNDs[0].childNDs:
            if max < nd.utc:
                max = nd.utc
                maxND = nd
        return [rnd.childNDs[0].pos, maxND.pos], maxND