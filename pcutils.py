import open3d as o3d
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class pcdutils:
    def __init__(self):
        super().__init__()
    def openpcd(self, name):
        pcd = o3d.io.read_point_cloud(name)
        downpcd = pcd.voxel_down_sample(voxel_size=0.1)
        return downpcd
    def get_pcd_2d(self, name):
        pcd = self.openpcd(name)
        pts = np.asanyarray(pcd.points)
        pts_2d = [[x,z] for x,y,z in pts if y<0.47]
        scaler = MinMaxScaler()
        pts_2d = scaler.fit_transform(pts_2d)
        pts_2d = [[int(w*900+100), int(h*400+50)] for h,w in pts_2d]

        return pts_2d

