import open3d as o3d
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class pcdutils:
    def __init__(self):
        super().__init__()
    def openpcd(self, name):
        pcd = o3d.io.read_point_cloud(name)
        return pcd
    def get_pcd_2d(self, name):
        pcd = self.openpcd(name)
        pts = np.asanyarray(pcd.points)
        pts_2d_x = [x for x,y,z in pts]
        pts_2d_y = [x for x,y,z in pts]
        pts_2d = [[x,y] for x,y,z in pts]
        scaler = MinMaxScaler()
        pts_2d = scaler.fit_transform(pts_2d)
        pts_2d = [[int(x*1000), int(y*500)] for x,y in pts_2d]
        print(pts_2d)
