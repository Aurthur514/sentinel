import threading
import time
import cv2
from typing import Dict
from datetime import datetime

class CameraWorker(threading.Thread):
    def __init__(self, camera_id:int, rtsp_url:str, on_frame, reconnect_interval=5):
        super().__init__(daemon=True)
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.on_frame = on_frame
        self.reconnect_interval = reconnect_interval
        self.running = True
        self.cap = None

    def run(self):
        while self.running:
            if self.cap is None:
                try:
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                except Exception:
                    self.cap = None
                    time.sleep(self.reconnect_interval)
                    continue
            if not self.cap.isOpened():
                self.cap.release()
                self.cap = None
                time.sleep(self.reconnect_interval)
                continue
            ret, frame = self.cap.read()
            if not ret or frame is None:
                # treat as disconnect and retry
                if self.cap:
                    try:
                        self.cap.release()
                    except Exception:
                        pass
                self.cap = None
                time.sleep(self.reconnect_interval)
                continue
            # call callback
            try:
                self.on_frame(self.camera_id, frame)
            except Exception:
                pass
            time.sleep(0.01)

    def stop(self):
        self.running = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass

class CameraManager:
    def __init__(self):
        self.workers: Dict[int, CameraWorker] = {}

    def start_camera(self, camera_id:int, rtsp_url:str, on_frame):
        if camera_id in self.workers:
            return
        w = CameraWorker(camera_id, rtsp_url, on_frame)
        self.workers[camera_id] = w
        w.start()

    def stop_camera(self, camera_id:int):
        w = self.workers.get(camera_id)
        if w:
            w.stop()
            del self.workers[camera_id]

    def stop_all(self):
        for k in list(self.workers.keys()):
            self.stop_camera(k)
