import cv2 as cv
import numpy as np
import datetime
from camera.sim_video import SimVideo



class Tracker:
    cv_box = [0,0,0,0]
    tracker = False

    def track(self, net_box, frame):
        if net_box == False:
            if self.tracker != False:
                ok, bbox = self.tracker.update(frame)
                if ok == True:
                    (x, y, w, h) = [int(v) for v in bbox]
                    self.cv_box = [x, y, x+w, y+h]
                else:
                    self.cv_box = [0,0,0,0]
                    self.tracker = False
        else:
            self.tracker = cv.legacy.TrackerMedianFlow_create()
            self.tracker.init(frame, (
                net_box[0],
                net_box[1],
                net_box[2]-net_box[0],
                net_box[3]-net_box[1]
            ))

def view_camera_video(child_conn, config):
    img = np.zeros([config.camera.width, config.camera.height, 3],dtype=np.uint8)
    img.fill(255)
    
    if config.run == "sim":
        from camera.camera_sim import SimModel
        model = SimModel(child_conn=child_conn, config=config)
        model.run()
    else:
        from camera.camera_jetson import JetsonModel
        model = JetsonModel(child_conn=child_conn, config=config)
        model.run()