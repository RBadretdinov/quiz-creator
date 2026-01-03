# Exact Steps to Deploy Your Quiz App

Follow these steps exactly to make your app publicly accessible (no installation needed for users).

## Step 1: Choose a Platform (Pick ONE)

I recommend **Render.com** - it's the easiest. Here's how:

## Step 2: Deploy to Render.com

### Step 2a: Create Account
1. Go to: **https://render.com**
2. Click **"Get Started for Free"** (top right)
3. Sign up with:
   - GitHub (recommended - you already have GitHub)
   - OR Email
4. Verify your email if needed

### Step 2b: Connect GitHub (if you signed up with GitHub, skip this)
1. In Render dashboard, click your profile (top right)
2. Click **"Account Settings"**
3. Go to **"Connected Accounts"** or **"GitHub"** section
4. Click **"Connect GitHub"** or **"Link GitHub Account"**
5. Authorize Render to access your repositories

### Step 2c: Create Web Service
1. In Render dashboard, click **"New +"** button (top right)
2. Click **"Web Service"**
3. You'll see "Connect a repository"
4. Click **"Connect account"** next to GitHub (if not connected)
5. Find and click on **"quiz-creator"** repository
6. Click **"Connect"**

### Step 2d: Configure Settings
Render will show a form. Fill it out like this:

**Name:**
```
quiz-creator
```
(or any name you want)

**Region:**
```
Oregon (US West)
```
(or closest to you)

**Branch:**
```
master
```
(should be auto-filled)

**Root Directory:**
```
(leave blank)
```

**Environment:**
```
Python 3
```
(should be auto-detected)

**Build Command:**
```
pip install -r requirements.txt
```
(copy this exactly)

**Start Command:**
```
uvicorn src.web_app:app --host 0.0.0.0 --port $PORT
```
(copy this exactly)

**Instance Type:**
```
Free
```
(click the Free option)

**Auto-Deploy:**
```
Yes
```
(checked - so it updates when you push to GitHub)

### Step 2e: Deploy
1. Scroll down and click **"Create Web Service"**
2. Wait 2-5 minutes (you'll see build logs)
3. You'll see "Live" when it's done!

### Step 2f: Get Your URL
1. Once it says "Live", you'll see your URL at the top
2. It will be something like: `https://quiz-creator-xxxx.onrender.com`
3. **Copy this URL** - this is your public website!

## Step 3: Test Your Deployed App

1. Click on your URL (or copy/paste into browser)
2. The website should load!
3. Try clicking around - it should work

## Step 4: Share with Users

Share your URL with anyone:
- They just visit the URL
- No installation needed
- Works on any device with a browser

## Troubleshooting

### If deployment fails:
1. Check the "Logs" tab in Render
2. Look for error messages
3. Common issues:
   - Wrong build/start commands → Check Step 2d above
   - Missing dependencies → Already in requirements.txt (should be fine)
   - Port issue → The $PORT is handled automatically

### If website doesn't load:
1. Make sure status says "Live" (green)
2. Try waiting 1-2 minutes (first load can be slow on free tier)
3. Check the logs for errors

### If you see errors on the website:
1. Check the "Logs" tab in Render
2. Look for Python errors
3. The free tier may "sleep" after 15 minutes of inactivity - first request after sleep takes 30-60 seconds

## What Happens Next?

- ✅ Your app is now PUBLIC
- ✅ Anyone can visit your URL
- ✅ No installation needed for users
- ✅ When you update code and push to GitHub, Render auto-updates (if auto-deploy is on)

## Quick Reference

**Your Repository:** https://github.com/RBadretdinov/quiz-creator

**Render Dashboard:** https://dashboard.render.com

**Your URL (after deployment):** https://quiz-creator-xxxx.onrender.com (you'll get this after Step 2f)

---

**That's it!** Your app is now publicly accessible! 🎉

