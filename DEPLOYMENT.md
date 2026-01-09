# SentinelSight Deployment Guide

This guide provides instructions for deploying SentinelSight to various cloud platforms.

## Prerequisites

- Git repository access
- Docker installed (for local testing)
- Account on chosen deployment platform

## Deployment Options

### 1. Render.com (Recommended for Quick Deploy)

Render is a modern cloud platform that offers free tier deployment with automatic builds.

**Steps:**

1. Fork this repository to your GitHub account
2. Sign up at [render.com](https://render.com)
3. Click "New +" and select "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` configuration
6. Click "Apply" to deploy

Your app will be available at `https://your-app-name.onrender.com`

**Configuration:**
- The `render.yaml` file is pre-configured
- Free tier available (service may spin down after inactivity)
- Environment variables can be set in Render dashboard

### 2. Railway.app

Railway offers simple deployment with generous free tier.

**Steps:**

1. Sign up at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select this repository
4. Railway will auto-detect the Dockerfile
5. Your app will be deployed automatically

**Configuration:**
- The `railway.json` file is pre-configured
- Add environment variable `PORT` (Railway sets this automatically)
- Add custom domain in Railway dashboard (optional)

### 3. Heroku

Heroku is a popular platform-as-a-service with straightforward deployment.

**Steps:**

1. Install Heroku CLI: `curl https://cli-assets.heroku.com/install.sh | sh`
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Deploy: `git push heroku main`

**Configuration:**
- The `Procfile` is pre-configured
- Set environment variables:
  ```bash
  heroku config:set LOITER_SECONDS=8
  ```

### 4. Docker Deployment (Self-Hosted)

Deploy on any server with Docker support.

**Steps:**

1. Clone repository:
   ```bash
   git clone https://github.com/Aurthur514/sentinel.git
   cd sentinel
   ```

2. Build Docker image:
   ```bash
   docker build -t sentinelsight:latest .
   ```

3. Run container:
   ```bash
   docker run -d -p 8000:8000 \
     -v $(pwd)/snapshots:/app/snapshots \
     --name sentinelsight \
     sentinelsight:latest
   ```

4. Access at `http://your-server-ip:8000`

**Using Docker Compose:**
```bash
docker-compose up -d
```

### 5. Cloud Providers (AWS, Azure, GCP)

For production deployments on major cloud providers:

#### AWS (Elastic Beanstalk)
1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init -p docker sentinel`
3. Create environment: `eb create sentinel-env`
4. Deploy: `eb deploy`

#### Azure (Container Instances)
```bash
az container create \
  --resource-group myResourceGroup \
  --name sentinelsight \
  --image your-registry/sentinelsight \
  --ports 8000 \
  --dns-name-label sentinelsight
```

#### Google Cloud Platform (Cloud Run)
```bash
gcloud run deploy sentinelsight \
  --source . \
  --platform managed \
  --allow-unauthenticated
```

## Environment Variables

Configure these environment variables based on your deployment:

- `LOITER_SECONDS`: Time in seconds before triggering loitering alert (default: 8)
- `PORT`: Port number for the web server (usually auto-set by platform)

## Post-Deployment

After deployment:

1. Access the web interface at your deployment URL
2. Test the health endpoint: `https://your-url/health`
3. Add a camera using the web UI or API
4. Configure zones for intrusion/loitering detection

## Monitoring & Scaling

### Health Check
The `/health` endpoint returns `{"status":"ok"}` and can be used for monitoring.

### Logs
- **Render/Railway/Heroku**: View logs in platform dashboard
- **Docker**: `docker logs sentinelsight`
- **Cloud providers**: Use native logging services

### Scaling Considerations
- **Database**: Current setup uses SQLite; for production, consider PostgreSQL
- **Storage**: Snapshots are stored locally; consider S3/blob storage for distributed deployments
- **Video Processing**: CPU-intensive; vertical scaling recommended

## Continuous Deployment

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:
- Runs on push to main branch
- Installs dependencies and tests
- Builds Docker image
- Runs health checks

To enable automatic deployments:
1. Add deployment platform credentials to GitHub Secrets
2. Update workflow to include deployment step
3. Push to main branch to trigger deployment

## Troubleshooting

### Port Issues
Ensure the `PORT` environment variable is set correctly. Most platforms auto-inject this.

### Missing Dependencies
If ultralytics fails to install, the app will fallback to basic motion detection.

### Video Access
When using RTSP cameras, ensure network access from deployment server to camera sources.

### Database
SQLite database persists in the container. For persistent storage:
- Mount volume: `-v /path/to/data:/app`
- Or use external database (PostgreSQL)

## Security Considerations

Before production deployment:
1. Add authentication (JWT, OAuth)
2. Use HTTPS/SSL certificates
3. Restrict API access with rate limiting
4. Store sensitive data in environment variables
5. Regular security updates

## Support

For issues or questions:
- GitHub Issues: [repository issues page]
- Documentation: See README.md

## Next Steps

Consider these enhancements:
- Add user authentication
- Implement webhook notifications
- Add clip recording/export
- Multi-model inference pipelines
- Horizontal scaling with message queue
