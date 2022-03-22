from fcntl import DN_DELETE
from logging import root

from matplotlib.pyplot import flag
from demo import MyWindow
import random, math

########Node class#############
# candiNDs = The nodes can be selected in policy
# childNDs = Already Expanded nodes, so, it has UTC value
class node:
    def __init__(self, pos=[0,0], vis=0, val=0, utc=0.0, leg=None, paND=None):
        self.pos = pos
        self.vis = vis
        self.val = val
        self.utc = utc
        self.leg = leg
        self.parentND = paND
        self.childNDs = []
        self.candiNDs = []

#########MCTS Class############
class standard_MCTS:
    def __init__(self, window, value_mcts, value_mcts_2):
        super().__init__()
        self.iterations = 100
        self.limit_l = value_mcts_2
        self.window = window

    def get_dist(self, pt1, pt2):
        x = pt2[0] - pt1[0]
        y = pt2[1] - pt1[1]
        d = math.sqrt((x*x)+(y*y))
        return x,d
    
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
        nd = node()
        for idx,pos in enumerate(spts):
            nd.childNDs.append(node(pos=pos,leg=idx, vis=1, paND=nd))
        nd.pos = self.get_robotCenter(spts)  
        return nd

    def get_candiND(self, nd, pts):
        for pt in pts:
            x, l = self.get_dist(nd.pos, pt)

            # policy 1 : Distance between two points are in workspace of each legs
            # policy 2 : Forward points should be selected
            if l < self.limit_l and x > 0:
                nd.candiNDs.append(node(pos=pt,leg=nd.leg, paND=nd))
        return nd

    def check_goal(self, pt, goal):
        x,y = pt
        x_min, x_max = goal[0], goal[0]+goal[2]
        y_min, y_max = goal[1], goal[1]+goal[3]
        if x_min<x<x_max  and y_min<y<y_max:
            return 1    
        else:
            return 0
        
    def findSimulPts(self, legs, pts):
        simulpts = []
        for idx,leg in enumerate(legs):
            temp = []
            for pt in pts:
                x,l = self.get_dist(leg,pt)

                # policy 1 : Distance between two points are in workspace of each legs
                # policy 2 : Forward points should be selected
                if l<self.limit_l and x>0:
                    templeg = legs[:]
                    templeg[idx] = pt
                    tempcenter = self.get_robotCenter(templeg)
                    _,d = self.get_dist(tempcenter, pt)
                    if d < self.limit_l:
                        temp.append(pt)
            simulpts.append(temp)
        return simulpts

    # UTC value function
    # w: N. of win , n: N. of visit in child node, t: N. of visit in parent node
    def utcFunc(self, nd):
        w, n, t = nd.val, nd.vis, nd.parentND.vis
        if n != 0:
            return float((w/n)+math.sqrt(2*math.log(t)/n))
        else:
            return 0
    def printND(self, nd):
        print(nd.pos, nd.vis, nd.val, nd.utc, nd.leg, len(nd.childNDs))

    # selection -> expansion -> simulation -> backpropagation -> final selection
    def mcts(self, spts, garea, pts):
        rootND = self.get_rootND(spts)
        for i in range(self.iterations):
            seleND = self.selection(rootND, pts)
            expaND = self.expansion(seleND)
            result = self.simulation(expaND, rootND, pts, garea)
            self.backprop(result, expaND)
        else:
            print("Iteration is done")
            self.finalSelect(rootND)
            return rootND

    def selection(self, nd, pts):
        if len(nd.candiNDs) == 0 and len(nd.childNDs) == 0:
            nd = self.get_candiND(nd, pts)
        
        if len(nd.candiNDs) == 0 and len(nd.childNDs) != 0:
            max = -100
            max_nd = node()
            for i in range(len(nd.childNDs)):
                if nd.childNDs[i].utc > max:
                    max_nd = nd.childNDs[i]
                    max = max_nd.utc
            snd = self.selection(max_nd, pts)
        else:
            snd = nd
        return snd
        
    def expansion(self, nd):
        end = nd.candiNDs[random.randrange(len(nd.candiNDs))]
        nd.childNDs.append(end)
        nd.candiNDs.remove(end)
        return end

    def simulation(self, end, rnd, pts, goal):
        legSet = [end.pos]
        for cnd in rnd.childNDs:
            if cnd.leg != end.leg:
                legSet.append(list(cnd.pos))
        robotCenter = self.get_robotCenter(legSet)
        
        while(1):
            if self.check_goal(robotCenter, goal) == 1:
                return 1
            else:
                ptsList = self.findSimulPts(legSet, pts)
                ptsSize = 0
                for leg in ptsList:
                    ptsSize += len(leg)
                
                if ptsSize == 0:
                    return 0
                else:
                    idx = random.randrange(ptsSize)
                    for legIdx, legList in enumerate(ptsList):
                        idxtemp = idx - len(legList)
                        if idxtemp < 0:
                            legSet[legIdx] = legList[idx]
                            robotCenter = self.get_robotCenter(legSet)
                            break
                        else:
                            idx = idxtemp

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
        maxLeg = 0
        for subrtND in rnd.childNDs:
            if max < subrtND.utc:
                max = subrtND.utc
                maxLeg = subrtND.leg
        max = -100
        maxidx = -100
        for idx, childND in enumerate(rnd.childNDs[maxLeg].childNDs):
            if max < childND.utc:
                max = childND.utc
                maxidx = idx
        rnd.childNDs[maxLeg] = childND
        legs = [n.pos for n in rnd.childNDs]
        rnd.pos = self.get_robotCenter(legs)
        
            
class momentum_MCTS:
    def __init__(self, value_mcts, value_mcts_2):
        super().__init__()
        self.iterations = value_mcts
        self.limit_l = value_mcts_2

    def get_dist(self, pt1, pt2):
        x = pt2[0] - pt1[0]
        y = pt2[1] - pt1[1]
        d = math.sqrt((x*x)+(y*y))
        return x,d

    # selection -> expansion -> simulation -> backpropagation -> final selection
    def mcts(self, spt, gpt, pts, type):
        # If goal point can be reached from start point in limited distance, return the goal node
        if  self.get_dist(spt, gpt)[1] < self.limit_l:
            print("Goal point is in the areas, so, program is terminated")
            return node(gpt, 0, 0, 0.0, None)

        root_nd = node(spt, 0, 0, 0.0, None)
        for i in range(self.iterations):
            se_node = self.selection(root_nd, pts)
            if len(se_node.childNDs) + len(se_node.candiNDs) == 0:
                if se_node.pos == gpt:
                    result = 1
                else:
                    result = 0
                self.backprop(result, se_node, gpt)
            else:
                ex_node = self.expansion(se_node)
                result = self.simulation(ex_node.pos, pts[:], gpt)
                self.backprop(result, ex_node, gpt)
        else:
            print("Iteration is done")
            final_node = self.finalSelect(root_nd, gpt)
            return final_node

    # input (center node, other points)
    def find_candidate(self, nd, pts):
        for i in range(len(pts)):
            x = pts[i][0] - nd.pos[0]
            y = pts[i][1] - nd.pos[1]
            l = math.sqrt((x*x)+(y*y))

            # policy 1 : Distance between two points are in limited distance
            # policy 2 : Forward points should be selected
            if l < self.limit_l and x > 0:
                nd.candiNDs.append(node(pts[i], 0, 0, 0.0, nd))
        return nd

    # Input (center node, other points)
    # center node is root node when it is first visit
    # Recursion algorithm is applied to find empty node
    def selection(self, cnd, pts):
        # If this node first visited, check the candidate nodes
        if len(cnd.candiNDs) == 0 and len(cnd.childNDs) == 0:
            cnd = self.find_candidate(cnd, pts)
            # This parent node doesn't have child node, so, the way is end.
            if len(cnd.candiNDs) == 0:
                return cnd
        # If candidate nodes are still remained, select this node
        # else, check the UTC values of child nodes, then, visit the childe node have maximum UTC value
        if len(cnd.candiNDs) != 0:
            snd = cnd
        else:
            max = -100
            max_nd = node()
            for i in range(len(cnd.childNDs)):
                if cnd.childNDs[i].utc > max:
                    max_nd = cnd.childNDs[i]
                    max = max_nd.utc
            snd = self.selection(max_nd, pts)
        return snd

    def expansion(self, snd):
        end = snd.candiNDs[random.randrange(len(snd.candiNDs))]
        snd.childNDs.append(end)
        snd.candiNDs.remove(end)
        return end

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

    # UTC value function
    # w: N. of win , n: N. of visit in child node, t: N. of visit in parent node
    def utcFunc(self, nd, gp):
        w, n, t = nd.val, nd.vis, nd.parentND.vis
        _, dist = self.get_dist(nd.parentND.pos, gp)
        return float((w/n)+math.sqrt(2*math.log(t)/n)/dist)

    def backprop(self, result, nd, gp):
        nd.vis += 1
        if result == 1:
            nd.val += 1
        if nd.parentND is not None:
            nd.parentND = self.backprop(result, nd.parentND, gp)
            for child in nd.parentND.childNDs:
                child.utc = self.utcFunc(child, gp)
        return nd

    def finalSelect(self, root_nd, gp):
        max = -100
        # print('\n')
        for i in range(len(root_nd.childNDs)):
            _, dist = self.get_dist(root_nd.childNDs[i].pos, gp)
            exploitation = root_nd.childNDs[i].val / root_nd.childNDs[i].vis/dist
            if exploitation > max:
                max_nd = root_nd.childNDs[i]
                max = exploitation
        if max == -100:
            return None
        else:
            return max_nd