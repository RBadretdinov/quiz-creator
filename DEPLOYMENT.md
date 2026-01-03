# Deployment Guide - Making Your Quiz App Public

## Understanding Deployment

Currently, your app runs locally (on your computer). To make it public so anyone can use it, you need to **deploy** it to a cloud server.

### How It Works:
- **You deploy once** to a cloud platform (free options available)
- **Users just visit the URL** - no installation needed
- **The server runs 24/7** on the cloud platform
- **Users don't need to install anything**

## Free Deployment Options

### Option 1: Render (Recommended - Easiest)

**Render.com** offers free hosting for web apps.

1. **Sign up**: Go to https://render.com (free account)
2. **Connect GitHub**:
   - Go to Dashboard > New > Web Service
   - Connect your GitHub account
   - Select your `quiz-creator` repository
3. **Configure**:
   - **Name**: `quiz-creator` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.web_app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. **Deploy**: Click "Create Web Service"
5. **Get your URL**: Render will give you a URL like `https://quiz-creator.onrender.com`

That's it! Your app will be public.

### Option 2: Railway

1. **Sign up**: https://railway.app (free tier available)
2. **New Project** > Deploy from GitHub repo
3. **Select repository**: `quiz-creator`
4. **Railway auto-detects** Python and runs it
5. **Get your URL**: Railway provides a URL automatically

### Option 3: Fly.io

1. **Install Fly CLI**: https://fly.io/docs/getting-started/installing-flyctl/
2. **Sign up**: `fly auth signup`
3. **Launch**: `fly launch` (in your project directory)
4. **Follow prompts** - Fly.io will guide you

### Option 4: PythonAnywhere (Free Tier)

1. **Sign up**: https://www.pythonanywhere.com (free account)
2. **Upload your code** via Web interface or Git
3. **Configure web app** in the Web tab
4. **Get your URL**: `yourusername.pythonanywhere.com`

## Files Needed for Deployment

I've created these files for you:

- **`Procfile`** - For Heroku/Render
- **`runtime.txt`** - Python version specification
- **`render.yaml`** - Render.com configuration

## Important: Database Considerations

Your app uses SQLite (local file database). For production:

### Option A: Keep SQLite (Simple)
- Works fine for small apps
- Data is stored on the server
- Free platforms may reset data on updates

### Option B: Use PostgreSQL (Better for production)
- More robust for production
- Free tier available on Render/Railway
- Requires code changes to switch databases

For now, SQLite is fine to get started!

## After Deployment

Once deployed:
1. **Share the URL** with users
2. **They can use it** without installing anything
3. **The server runs 24/7** (on free tier, may sleep after inactivity)
4. **You can update** by pushing to GitHub (auto-deploys)

## Free Tier Limitations

Free tiers typically have:
- App may sleep after inactivity (takes a few seconds to wake up)
- Limited resources (usually fine for small apps)
- Some platforms have usage limits

## Recommended: Render.com

I recommend **Render.com** because:
- ✅ Free tier available
- ✅ Easy to set up
- ✅ Auto-deploys from GitHub
- ✅ Good documentation
- ✅ PostgreSQL available (if needed later)

## Next Steps

1. Choose a platform (I recommend Render)
2. Sign up for free account
3. Connect your GitHub repository
4. Deploy!
5. Share your URL with users

Need help with a specific platform? Let me know!

