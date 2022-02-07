import cv2
import numpy as np

def make_ground():
    bg = np.zeros((1000,1000,3),np.uinit8)
    return bg

class TreeSearch:
    def __init__(self): 
        pass
    def mtcs(self):
        print('Start MTCS')
        bg = np.full((800,1500,3),255,np.uint8)
        cv2.imshow('Window', bg)
        cv2.waitKey(0)

if __name__ == "__main__":
    TS = TreeSearch()
    TS.mtcs()
    print('Start MTCS')
    print('Start MTCS')
    cv2.destroyAllWindows()

