import time
import os
import cv2
import threading
from typing import Callable, Dict, Any, List

# Try to import ultralytics YOLO, otherwise fallback
try:
    from ultralytics import YOLO
    HAS_YOLO = True
except Exception:
    HAS_YOLO = False

class InferenceEngine:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = None
        self.model_path = model_path
        if HAS_YOLO:
            try:
                self.model = YOLO(self.model_path)
            except Exception:
                self.model = None

    def detect(self, frame):
        # returns list of detections: {label, conf, bbox}
        if self.model:
            results = self.model(frame)[0]
            dets = []
            for r in results.boxes.data.tolist():
                # r = [x1,y1,x2,y2,score,class]
                x1,y1,x2,y2,conf,cls = r
                label = self.model.names[int(cls)] if hasattr(self.model,'names') else str(int(cls))
                dets.append({'label':label,'confidence':float(conf),'bbox':{'x1':x1,'y1':y1,'x2':x2,'y2':y2}})
            return dets
        # fallback simple motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21,21), 0)
        if not hasattr(self, '_bg'):
            self._bg = gray
            return []
        frameDelta = cv2.absdiff(self._bg, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        cnts,_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dets = []
        for c in cnts:
            if cv2.contourArea(c) < 500:
                continue
            x,y,w,h = cv2.boundingRect(c)
            dets.append({'label':'motion','confidence':0.5,'bbox':{'x1':x,'y1':y,'x2':x+w,'y2':y+h}})
        # slowly adapt background
        self._bg = cv2.addWeighted(self._bg,0.9,gray,0.1,0)
        return dets
