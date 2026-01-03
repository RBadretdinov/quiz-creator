# Migration to Web Application

The Quiz Application has been successfully converted from a console-based application to a web-based application using FastAPI. This makes testing much easier and provides a modern web interface.

## What Changed

### New Files Created

1. **`src/web_app.py`** - FastAPI application with REST API endpoints
2. **`web/index.html`** - Modern web frontend with HTML, CSS, and JavaScript
3. **`run_web.py`** - Script to run the web server
4. **`WEB_SETUP.md`** - Setup and usage guide for the web version
5. **`web/static/`** - Directory for static files (CSS, JS, images)

### Files Modified

1. **`requirements.txt`** - Added web dependencies:
   - `fastapi==0.104.1` - Web framework
   - `uvicorn[standard]==0.24.0` - ASGI server
   - `python-multipart==0.0.6` - File uploads support

### What Stayed the Same

- All business logic remains unchanged
- Database structure and schema unchanged
- All existing models, managers, and engines work as before
- Data files and database location unchanged

## Architecture

The web application follows a clean separation of concerns:

```
┌─────────────────┐
│  Web Frontend   │  (HTML/CSS/JavaScript)
│   (Browser)     │
└────────┬────────┘
         │ HTTP/REST API
         │
┌────────▼────────┐
│   FastAPI App   │  (src/web_app.py)
│   REST API      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Business Logic │  (Existing managers, engines)
│  - QuestionMgr  │
│  - TagManager   │
│  - QuizEngine   │
│  - Analytics    │
└────────┬────────┘
         │
┌────────▼────────┐
│   SQLite DB     │  (data/quiz.db)
└─────────────────┘
```

## Benefits of Web Version

1. **Easier Testing**
   - Test with HTTP requests (curl, Postman, pytest)
   - Browser automation (Selenium, Playwright)
   - API testing tools
   - No need for terminal interaction mocking

2. **Better User Experience**
   - Modern web interface
   - Responsive design
   - No terminal required
   - Accessible from any device on the network

3. **API-First Design**
   - RESTful API enables integration
   - Can build mobile apps or other clients
   - Easy to extend with new features

4. **Development Benefits**
   - Hot reload during development
   - Better debugging tools
   - Standard web development workflow

## Running the Application

### Console Version (Original)
```bash
python src/main.py
```

### Web Version (New)
```bash
python run_web.py
```

Then open: http://127.0.0.1:8000

## API Endpoints

All endpoints are documented in `WEB_SETUP.md`. Key endpoints:

- `GET /api/questions` - List questions
- `POST /api/questions` - Create question
- `GET /api/tags` - List tags
- `POST /api/quiz/start` - Start quiz
- `GET /api/analytics/overview` - Get analytics

## Testing Strategy

Now that it's a web app, you can test it in multiple ways:

1. **Manual Testing**: Use the web interface in a browser
2. **API Testing**: Use curl, Postman, or HTTPie
3. **Automated Testing**: Write pytest tests that make HTTP requests
4. **Browser Automation**: Use Selenium or Playwright for end-to-end tests

Example API test:
```python
import requests

response = requests.get("http://127.0.0.1:8000/api/questions")
assert response.status_code == 200
questions = response.json()
```

## Next Steps

1. **Add Authentication**: Implement user authentication and authorization
2. **Session Management**: Proper session handling for quiz sessions
3. **Real-time Updates**: WebSocket support for live updates
4. **Enhanced UI**: Improve the frontend with a framework like React or Vue
5. **Testing Suite**: Create comprehensive API tests
6. **Production Deployment**: Set up for production (see WEB_SETUP.md)

## Backward Compatibility

The console version (`src/main.py`) still works and has not been modified. You can use either:
- Console version for terminal-based usage
- Web version for web-based usage

Both share the same database, so data is compatible between versions.

