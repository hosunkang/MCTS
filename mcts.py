from logging import root
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
        self.leg_num = leg
        self.parentND = paND
        self.childNDs = []
        self.candiNDs = []

#########MCTS Class############
class standard_MCTS:
    def __init__(self, value_mcts, value_mcts_2):
        super().__init__()
        self.iterations = 10
        self.limit_l = value_mcts_2

    def get_dist(self, pt1, pt2):
        x = pt2[0] - pt1[0]
        y = pt2[1] - pt1[1]
        d = math.sqrt((x*x)+(y*y))
        return x,d
    def get_rootNode(self, spts):
        x_sum = 0
        y_sum = 0
        for x,y in spts:
            x_sum += x
            y_sum += y
        else:
            pos = [x_sum/len(spts),y_sum/len(spts)]
            nd = node(pos, 0, 0, 0.0, None, None)
        return nd

    # selection -> expansion -> simulation -> backpropagation -> final selection
    def mcts(self, spts, garea, pts, robot):
        rootND = self.get_rootNode(spts)
        print(rootND.pos)
        for i in range(self.iterations):
            self.selection(rootND, pts, robot)
    
    def find_candi(self, nd, pts):
        for i in range(len(pts)):
            x = pts[i][0] - nd.pos[0]
            y = pts[i][1] - nd.pos[1]
            l = math.sqrt((x*x)+(y*y))

            # policy 1 : Distance between two points are in workspace of each legs
            # policy 2 : Forward points should be selected
            if l < self.limit_l and x > 0:
                nd.candiNDs.append(node(pts[i], 0, 0, 0.0, nd))
        return nd

    def selection(self, rnd, pts, robot):
        rnd = self.find_candidate(rnd, pts)
        print(rnd.candiNDs)



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