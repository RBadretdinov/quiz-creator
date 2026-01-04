# Backend/Server Version (Python)

This folder contains the **Python backend/server version** of the Quiz Application.

## ⚠️ Note

This is **NOT used by the static version** on GitHub Pages. The static version uses `web/index.html` only.

This backend version is kept for:
- Future use if you want to deploy a server version
- Running locally with a Python server
- Console application (uses files in `src/`)

## Files in This Folder

- `web_app.py` - FastAPI web server application
- `run_web.py` - Script to run the web server locally
- `Procfile`, `render.yaml`, `runtime.txt` - Deployment configurations (for Render, Heroku, etc.)

## How to Use (If Needed)

### Run Locally
```bash
cd backend
python run_web.py
```

### Deploy to Cloud
Use the deployment configs (Procfile, render.yaml) with services like Render or Heroku.

## Current Setup

The **static version** (in `web/index.html`) is what's currently deployed and used. This backend folder is kept for reference/future use but is not required.

