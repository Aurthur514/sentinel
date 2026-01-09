# SentinelSight — AI Video Analytics (MVP)

This repository contains a 2-day sprint MVP for a multi-camera video analytics platform.

## Deploy Now

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/sentinel)
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Quick Start (Local)

1. Create virtualenv and install:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Open http://localhost:8000

## Docker (Recommended Quick Test)

1. Fetch a small sample video (Linux/macOS):

```bash
./scripts/download_sample.sh
```

Windows PowerShell:

```powershell
.\scripts\download_sample.ps1
```

2. Build and run with docker-compose:

```bash
docker-compose up --build
```

3. Add the sample video as a camera (inside container path):

```bash
curl -X POST http://localhost:8000/cameras -H "Content-Type: application/json" -d "{\"name\":\"LocalSample\",\"rtsp_url\":\"/app/test_videos/sample.mp4\",\"location\":\"Local\"}"
```

4. Open the UI: http://localhost:8000 and watch events appear as motion/intrusion/loitering.

## Deploy to Cloud

SentinelSight can be easily deployed to various cloud platforms:

- **Render.com**: One-click deploy with the included `render.yaml`
- **Railway.app**: Auto-deploy from GitHub with `railway.json`
- **Heroku**: Deploy with `Procfile` configuration
- **Docker**: Self-host on any server with Docker support

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for each platform.

## API Usage

**Add a camera:**
```bash
POST /cameras
Content-Type: application/json

{
  "name": "Camera1",
  "rtsp_url": "rtsp://...",
  "location": "Site A"
}
```

**Get events:**
```bash
GET /events?camera_id=1&rule=intrusion
```

**Set zones:**
```bash
POST /cameras/1/zones
Content-Type: application/json

{
  "zone1": {"x1": 100, "y1": 100, "x2": 500, "y2": 400}
}
```

## Testing Without RTSP

You can use a local video file by using a file path in `rtsp_url`.

## Features

- Real-time video analytics with YOLO object detection
- Motion detection and intrusion alerts
- Loitering detection with configurable thresholds
- Zone-based event triggering
- Event snapshot capture and storage
- Web UI for camera management and event monitoring

## Known Limitations

- Uses ultralytics YOLO if installed; otherwise falls back to simple motion detection.
- Loitering detection uses a simple centroid tracker (best-effort).
- SQLite database (suitable for MVP; consider PostgreSQL for production)

## Next Steps (If Extended)

- Add role-based access and authentication
- MQTT/webhook publishing for events
- Clip recording and export functionality
- Robust multi-model inference pipelines
- Horizontal scaling with message queues
