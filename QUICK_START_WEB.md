# Quick Start - Web Application

## 1. Install Dependencies

First, make sure you have all the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- uvicorn (ASGI server)
- All other dependencies

## 2. Test Locally

Run the web server:

```bash
python run_web.py
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## 3. Open in Browser

Open your web browser and go to:
```
http://127.0.0.1:8000
```

You should see the Quiz Application web interface!

## 4. Test the API

You can also test the API directly:

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Get all questions
curl http://127.0.0.1:8000/api/questions

# Get statistics
curl http://127.0.0.1:8000/api/stats
```

## 5. Create GitHub Repository

See `GITHUB_SETUP.md` for detailed instructions.

Quick version:
1. Go to https://github.com/new
2. Create repository named `quiz-app` (or your preferred name)
3. **Don't** initialize with README/gitignore
4. Run:
   ```bash
   git remote add origin https://github.com/RBadretdinov/quiz-app.git
   git push -u origin master
   ```

## Troubleshooting

### Port Already in Use
If port 8000 is busy, edit `run_web.py` and change the port:
```python
uvicorn.run(..., port=8001)
```

### Module Not Found
Make sure you're in the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Then install dependencies again.

### Database Errors
The database will be created automatically on first run in the `data/` directory.

