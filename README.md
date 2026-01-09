<<<<<<< HEAD
# SentinelSight — AI Video Analytics (MVP)

This repository contains a 2-day sprint MVP for a multi-camera video analytics platform.

Quick start (local):

1. Create virtualenv and install:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Open http://localhost:8000

Docker (recommended quick test):

1. Fetch a small sample video (Linux/macOS):

```bash
./scripts/download_sample.sh
```

Windows PowerShell:

```powershell
.\scripts\download_sample.ps1
```

2. Build and run with docker-compose:

```powershell
docker-compose up --build
```

3. Add the sample video as a camera (inside container path):

```powershell
curl -X POST http://localhost:8000/cameras -H "Content-Type: application/json" -d "{\"name\":\"LocalSample\",\"rtsp_url\":\"/app/test_videos/sample.mp4\",\"location\":\"Local\"}"
```

4. Open the UI: http://localhost:8000 and watch events appear as motion/intrusion/loitering.

How to add a camera:
- POST /cameras with JSON: {"name":"Camera1","rtsp_url":"rtsp://...","location":"Site A"}

Testing without RTSP:
- You can use a local video file by using a file path in `rtsp_url`.

Known limitations:
- Uses ultralytics YOLO if installed; otherwise falls back to simple motion detection.
- Loitering detection uses a simple centroid tracker (best-effort).

Next steps (if extended):
- Add role-based access, MQTT/webhook publishing, clip recording, robust multi-model inference, and horizontal scaling.
=======
# sentinel
sentine
>>>>>>> 8696aebe72b73cf45931a76209bfc034d85b3a70
