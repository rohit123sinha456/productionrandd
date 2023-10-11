#Detectiona and tracking of Sudisa Helmet model
#https://github.com/mikel-brostrom/yolo_tracking
import os
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
from boxmot import DeepOCSORT
import yaml
import collections

class Infer:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.tracker_model = self.config['models']['tracker']
        self.detection_model = self.config['models']['detection']
        self.tracker = DeepOCSORT(
            model_weights=Path(self.tracker_model), # which ReID model to use
            device='cpu',
            fp16=False,
            per_class=False
        )
        self.ModelPath = os.path.join('.', self.detection_model, 'best.pt')
        self.Model = YOLO(self.ModelPath)
        self.threshold = 0.5
        self.ClassName = {0: 'Helmet', 1: 'No Helmet'}
        self.color = (0,0,255)
        self.thickness = 2
        self.fontscale = 0.5
        # Generate output
        self.new_nonhelmet = collections.deque(maxlen=50)

    def detection(self,Frame):
        results = self.Model.predict(Frame,verbose=False)
        detection = []
        for result in results:
            boxes = result.boxes
            classes = boxes.cls
            confidence = boxes.conf
            for idx, box in enumerate(boxes.xyxy):
                x1, y1, x2, y2 = box
                c1 = int(x1.item())
                c2 = int(y1.item())
                c3 = int(x2.item())
                c4 = int(y2.item())
                detection.append([c1,c2,c3,c4,confidence[idx].item(),int(classes[idx].item())])
        return detection
    
    def tracking(self,Frame,detection):
        try:
            tracks = self.tracker.update(np.array(detection), Frame) # --> (x, y, x, y, id, conf, cls, ind)
            
            xyxys = tracks[:, 0:4].astype('int') # float64 to int
            ids = tracks[:, 4].astype('int') # float64 to int
            confs = tracks[:, 5]
            clss = tracks[:, 6].astype('int') # float64 to int
        except Exception as e:
            # print(e)
            return None
        # print(tracks)
        if tracks.shape[0] != 0:
            for xyxy, id, conf, cls in zip(xyxys, ids, confs, clss):
                if(cls == 0):
                    color = (0,255,0)
                else:
                    color = (0,0,255) # Red for no Helmet
                    if(id not in self.new_nonhelmet):
                        self.new_nonhelmet.append(id)
                        # print(self.new_nonhelmet)
                        Frame = cv2.rectangle(
                            Frame,
                            (xyxy[0], xyxy[1]),
                            (xyxy[2], xyxy[3]),
                            color,
                            self.thickness
                        )
                        return Frame
        return None