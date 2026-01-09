import os
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from sqlmodel import select
from datetime import datetime
import cv2
import io
import base64

from .db import init_db, get_session
from .models import Camera, Event
from .camera_manager import CameraManager
from .inference import InferenceEngine

app = FastAPI(title='SentinelSight')
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__),'templates'))
app.mount('/static', StaticFiles(directory=os.path.join(os.path.dirname(__file__),'static')), name='static')

init_db()
cm = CameraManager()
engine = InferenceEngine()

# in-memory latest frames
_latest_frames = {}
# per-camera trackers for loitering detection
_trackers = {}  # camera_id -> {track_id: {'first_seen':dt,'last_seen':dt,'bbox':{},'reported':bool}}
LOITER_SECONDS = int(os.environ.get('LOITER_SECONDS', '8'))
SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'snapshots')
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

class CameraIn(BaseModel):
    name: str
    rtsp_url: str
    location: Optional[str] = None
    zones: Optional[dict] = {}

@app.on_event('startup')
def startup():
    # resume cameras from DB
    with get_session() as s:
        cams = s.exec(select(Camera)).all()
        for c in cams:
            cm.start_camera(c.id, c.rtsp_url, on_frame)

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request':request})

@app.post('/cameras')
def add_camera(payload: CameraIn):
    cam = Camera(name=payload.name, rtsp_url=payload.rtsp_url, location=payload.location, zones=payload.zones)
    with get_session() as s:
        s.add(cam); s.commit(); s.refresh(cam)
    cm.start_camera(cam.id, cam.rtsp_url, on_frame)
    return cam

@app.get('/cameras')
def list_cameras():
    with get_session() as s:
        cams = s.exec(select(Camera)).all()
        return cams

@app.get('/cameras/{camera_id}/snapshot')
def snapshot(camera_id:int):
    frame = _latest_frames.get(camera_id)
    if frame is None:
        raise HTTPException(status_code=404, detail='No snapshot')
    _, buf = cv2.imencode('.jpg', frame)
    return StreamingResponse(io.BytesIO(buf.tobytes()), media_type='image/jpeg')

@app.get('/events')
def get_events(camera_id: Optional[int]=None, rule: Optional[str]=None, start: Optional[str]=None, end: Optional[str]=None):
    with get_session() as s:
        q = select(Event)
        if camera_id:
            q = q.where(Event.camera_id==camera_id)
        if rule:
            q = q.where(Event.rule==rule)
        if start:
            sd = datetime.fromisoformat(start)
            q = q.where(Event.timestamp >= sd)
        if end:
            ed = datetime.fromisoformat(end)
            q = q.where(Event.timestamp <= ed)
        evs = s.exec(q).all()
        return evs

@app.get('/events/{event_id}')
def get_event(event_id:int):
    with get_session() as s:
        ev = s.get(Event, event_id)
        if not ev:
            raise HTTPException(status_code=404)
        return ev


@app.get('/events/{event_id}/snapshot')
def event_snapshot(event_id: int):
    with get_session() as s:
        ev = s.get(Event, event_id)
        if not ev or not ev.snapshot_path:
            raise HTTPException(status_code=404, detail='Snapshot not found')
        # serve the snapshot file
        if not os.path.exists(ev.snapshot_path):
            raise HTTPException(status_code=404, detail='Snapshot file missing')
        return FileResponse(ev.snapshot_path, media_type='image/jpeg', filename=os.path.basename(ev.snapshot_path))

# callback from camera manager
from .db import get_session

def on_frame(camera_id:int, frame):
    # store latest
    _latest_frames[camera_id] = frame.copy()
    # run detection
    dets = engine.detect(frame)
    # simple rule: if detection label person or motion intersects zones -> intrusion
    from .db import get_session
    from .models import Event, Camera
    with get_session() as s:
        cam = s.get(Camera, camera_id)
        if cam:
            cam.status = 'online'
            cam.last_frame_time = datetime.utcnow()
            s.add(cam); s.commit()
        # check zones
        zones = cam.zones or {}
        # ensure tracker structure
        if camera_id not in _trackers:
            _trackers[camera_id] = {}

        # helper to save snapshot and return path
        def _save_snapshot(cam_id, track_or_event_id=None):
            ts = datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')
            fname = f"cam{cam_id}_{ts}.jpg" if track_or_event_id is None else f"cam{cam_id}_{track_or_event_id}_{ts}.jpg"
            path = os.path.join(SNAPSHOT_DIR, fname)
            try:
                cv2.imwrite(path, frame)
                return path
            except Exception:
                return None

        # process detections: intrusion and tracker-based loitering
        for d in dets:
            label = d.get('label')
            bbox = d.get('bbox')
            conf = d.get('confidence')

            # intrusion: if any zone and bbox centroid inside zone
            for zname, z in (zones.items() if isinstance(zones, dict) else []):
                try:
                    zx1,zy1,zx2,zy2 = z['x1'], z['y1'], z['x2'], z['y2']
                    cx = (bbox['x1']+bbox['x2'])/2
                    cy = (bbox['y1']+bbox['y2'])/2
                    if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                        snap = _save_snapshot(camera_id, 'intrusion')
                        ev = Event(camera_id=camera_id, rule='intrusion', object_type=label, confidence=conf, bbox=bbox, snapshot_path=snap)
                        s.add(ev); s.commit(); s.refresh(ev)
                except Exception:
                    continue

            # simple centroid-based tracker for loitering within zones
            if label is None:
                continue
            # only consider people or motion for loitering
            if label.lower() not in ('person', 'motion'):
                continue

            # compute centroid
            try:
                cx = (bbox['x1']+bbox['x2'])/2
                cy = (bbox['y1']+bbox['y2'])/2
            except Exception:
                continue

            # match to existing tracks
            tracks = _trackers[camera_id]
            matched_id = None
            min_dist = 1e9
            for tid, t in tracks.items():
                tb = t.get('bbox')
                tcx = (tb['x1']+tb['x2'])/2
                tcy = (tb['y1']+tb['y2'])/2
                dist = ((tcx-cx)**2 + (tcy-cy)**2)**0.5
                if dist < min_dist:
                    min_dist = dist; matched_id = tid

            if matched_id is None or min_dist > 80:
                # new track
                new_id = max(list(tracks.keys())+[0]) + 1
                tracks[new_id] = {'first_seen': datetime.utcnow(), 'last_seen': datetime.utcnow(), 'bbox': bbox, 'reported': False}
                tid = new_id
            else:
                tid = matched_id
                tracks[tid]['last_seen'] = datetime.utcnow()
                tracks[tid]['bbox'] = bbox

            # if track has stayed more than LOITER_SECONDS and not yet reported -> create loitering event
            t = tracks[tid]
            duration = (t['last_seen'] - t['first_seen']).total_seconds()
            if duration >= LOITER_SECONDS and not t.get('reported'):
                # ensure centroid inside a zone for loitering
                in_zone = False
                for zname, z in (zones.items() if isinstance(zones, dict) else []):
                    try:
                        zx1,zy1,zx2,zy2 = z['x1'], z['y1'], z['x2'], z['y2']
                        tcx = (t['bbox']['x1']+t['bbox']['x2'])/2
                        tcy = (t['bbox']['y1']+t['bbox']['y2'])/2
                        if zx1 <= tcx <= zx2 and zy1 <= tcy <= zy2:
                            in_zone = True; break
                    except Exception:
                        continue
                if in_zone:
                    snap = _save_snapshot(camera_id, f'loiter_{tid}')
                    ev = Event(camera_id=camera_id, rule='loitering', object_type=label, confidence=conf, bbox=t['bbox'], snapshot_path=snap)
                    s.add(ev); s.commit(); s.refresh(ev)
                    tracks[tid]['reported'] = True

@app.post('/cameras/{camera_id}/zones')
def set_zones(camera_id:int, payload: dict):
    with get_session() as s:
        cam = s.get(Camera, camera_id)
        if not cam:
            raise HTTPException(status_code=404)
        cam.zones = payload
        s.add(cam); s.commit(); s.refresh(cam)
        return cam

# simple health
@app.get('/health')
def health():
    return {'status':'ok'}
