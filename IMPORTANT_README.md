# Important: Repository and Testing Info

## 📍 Where is the GitHub Repository?

**I cannot create the GitHub repository for you** - I can only prepare your code and give you instructions. You need to create it yourself on GitHub.

### To Create the Repository:

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `quiz-app` (or any name you prefer)
3. **Description**: "A comprehensive quiz application with web interface"
4. **Choose**: Public or Private
5. **IMPORTANT**: Do NOT check "Initialize with README" (we already have files)
6. **Click**: "Create repository"

### Then Push Your Code:

After creating the repository, GitHub will show you commands. Run these:

```bash
git remote add origin https://github.com/RBadretdinov/quiz-app.git
git push -u origin master
```

## 📁 Where is index.html?

The `index.html` file is located at:
```
C:\dev\quiz\web\index.html
```

**Full path**: `C:\dev\quiz\web\index.html`

## ⚠️ Important: How to Test Locally

**You cannot just drag `index.html` into a browser** - it needs to be served by the FastAPI server because:
1. The HTML makes API calls to `/api/...` endpoints
2. These endpoints only work when the web server is running
3. Opening the file directly won't have access to the API

### Correct Way to Test:

1. **Start the web server**:
   ```bash
   python run_web.py
   ```

2. **Open in browser**:
   ```
   http://127.0.0.1:8000
   ```

   The FastAPI server will automatically serve the `index.html` file when you visit the root URL.

### Alternative: If You Just Want to See the HTML

If you want to see the HTML structure without the API, you can:
- Open `web\index.html` in a browser
- But the API calls won't work (you'll see errors in the browser console)
- The page won't be functional

## 🚀 Quick Test Steps

```bash
# 1. Make sure dependencies are installed
pip install -r requirements.txt

# 2. Start the server
python run_web.py

# 3. Open browser to:
# http://127.0.0.1:8000
```

The server will serve the HTML file automatically!

