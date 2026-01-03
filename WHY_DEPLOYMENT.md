# Why You Need Deployment (vs GitHub Pages)

## The Difference

### Your Portfolio (GitHub Pages works!)
- **Type:** Static website
- **Files:** HTML, CSS, JavaScript
- **How it works:** Browser downloads files, runs JavaScript in browser
- **No server needed:** GitHub Pages just serves files
- ✅ GitHub Pages can host this

### Your Quiz App (Needs a server)
- **Type:** Dynamic web application
- **Backend:** Python + FastAPI server
- **Database:** SQLite database file
- **API:** Server processes requests, stores data
- **How it works:** Browser talks to Python server via API
- ❌ GitHub Pages **cannot** run Python servers

## Why Your Quiz App Needs a Server

1. **Database Storage**
   - Questions, tags, quiz sessions stored in SQLite
   - GitHub Pages can't run databases
   - Need a server to read/write database

2. **Backend Processing**
   - Creating questions, scoring quizzes, analytics
   - Python code runs on server
   - GitHub Pages only serves files (no code execution)

3. **API Endpoints**
   - `/api/questions`, `/api/tags`, `/api/quiz/start`
   - These need a Python server to handle requests
   - GitHub Pages doesn't run servers

## Your Options

### Option 1: Deploy to Cloud Platform (Recommended)
- **Pros:** Full functionality, users just visit URL
- **Cons:** Need external service (but free!)
- **Services:** Render, Railway, Fly.io (all free)
- **Time:** 5 minutes to set up

### Option 2: Make Static Version (Limited)
- **Pros:** Can use GitHub Pages, no external service
- **Cons:** No database, no backend, data stored in browser only
- **What you'd lose:**
  - Persistent storage (data lost on refresh)
  - No sharing between users
  - Limited functionality
- **Time:** Hours to rewrite

### Option 3: Keep Local Only
- **Pros:** No setup needed
- **Cons:** Users must install Python, dependencies, run server
- **Not ideal for:** Public use

## The Bottom Line

**GitHub Pages = Files only (like your portfolio)**
**Your Quiz App = Needs a server (like a real web app)**

That's why you need deployment to a platform that runs servers!

## But Don't Worry!

- **Render.com is FREE** (and takes 5 minutes)
- **It's just like GitHub Pages** but for apps that need servers
- **Users don't install anything** - they just visit your URL
- **It auto-deploys from GitHub** (just like GitHub Pages!)

Think of it like this:
- GitHub Pages = Hosting your portfolio files
- Render = Hosting your app's server + files

Both are free, both are easy! 🎉

