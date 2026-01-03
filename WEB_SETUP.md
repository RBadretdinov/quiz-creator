# Web Application Setup Guide

The Quiz Application has been converted to a web-based application using FastAPI. This makes it easier to test and provides a modern web interface.

## Quick Start

### 1. Install Dependencies

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

### 2. Run the Web Server

#### Option 1: Using the run script (Recommended)
```bash
python run_web.py
```

#### Option 2: Using uvicorn directly
```bash
cd src
uvicorn web_app:app --reload --host 127.0.0.1 --port 8000
```

### 3. Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

You should see the Quiz Application web interface!

## API Endpoints

The web application provides a REST API at `/api/`:

### Questions
- `GET /api/questions` - List all questions (with optional search, filtering)
- `GET /api/questions/{question_id}` - Get a specific question
- `POST /api/questions` - Create a new question
- `PUT /api/questions/{question_id}` - Update a question
- `DELETE /api/questions/{question_id}` - Delete a question

### Tags
- `GET /api/tags` - List all tags
- `GET /api/tags/{tag_id}` - Get a specific tag
- `POST /api/tags` - Create a new tag
- `DELETE /api/tags/{tag_id}` - Delete a tag

### Quiz
- `POST /api/quiz/start` - Start a new quiz session
- `POST /api/quiz/submit` - Submit an answer for a quiz question

### Analytics
- `GET /api/analytics/overview` - Get analytics overview
- `GET /api/stats` - Get general statistics

### Health Check
- `GET /api/health` - Check if the API is running

## Testing the API

You can test the API using curl, Postman, or any HTTP client:

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Get all questions
curl http://127.0.0.1:8000/api/questions

# Create a question
curl -X POST http://127.0.0.1:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is the capital of France?",
    "question_type": "multiple_choice",
    "answers": [
      {"text": "Paris", "is_correct": true},
      {"text": "London", "is_correct": false},
      {"text": "Berlin", "is_correct": false}
    ],
    "tags": ["geography", "europe"]
  }'
```

## Development

### Auto-reload

The web server runs with auto-reload enabled by default (using `--reload` flag). Any changes to the Python code will automatically restart the server.

### Database

The web application uses the same SQLite database as the console version. Data is stored in `data/quiz.db`.

### Static Files

The web frontend is served from the `web/` directory. Static files (CSS, JS, images) should be placed in `web/static/`.

## Differences from Console Version

- **User Interface**: Web browser instead of terminal
- **Testing**: Easier to test with HTTP requests and browser automation
- **Access**: Can be accessed from multiple devices on the same network
- **API**: REST API allows integration with other applications

## Production Deployment

For production deployment, consider:

1. **Use a production ASGI server**: Use gunicorn with uvicorn workers
   ```bash
   gunicorn web_app:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set up a reverse proxy**: Use nginx or Apache to serve static files and proxy API requests

3. **Enable HTTPS**: Use SSL/TLS certificates for secure connections

4. **Configure CORS**: Update CORS settings in `web_app.py` to only allow specific origins

5. **Use environment variables**: Store configuration in environment variables instead of hardcoding

6. **Set up logging**: Configure proper logging for production environments

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, change it:
```python
# In run_web.py or uvicorn command
port=8001  # Use a different port
```

### Database Errors
Make sure the `data/` directory exists and is writable:
```bash
mkdir -p data
chmod 755 data
```

### Import Errors
Make sure you're running from the project root directory and that all dependencies are installed.

## Next Steps

- Add user authentication
- Implement session management for quizzes
- Add real-time updates
- Improve error handling and validation
- Add more analytics and reporting features

