import random, math

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