# GitHub Repository Setup Guide

This guide will help you create a new GitHub repository and push your Quiz Application code to it.

## Step 1: Create the GitHub Repository

You have two options:

### Option A: Using GitHub Web Interface (Recommended)

1. Go to https://github.com/new
2. Repository name: `quiz-app` (or any name you prefer)
3. Description: "A comprehensive quiz application with web interface, built with Python and FastAPI"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

### Option B: Using GitHub CLI (if installed)

```bash
gh repo create quiz-app --public --description "A comprehensive quiz application with web interface, built with Python and FastAPI"
```

## Step 2: Add Remote and Push

After creating the repository, GitHub will show you the commands. Run these in your terminal:

```bash
# Add the remote repository
git remote add origin https://github.com/RBadretdinov/quiz-app.git

# Or if you prefer SSH:
# git remote add origin git@github.com:RBadretdinov/quiz-app.git

# Verify the remote was added
git remote -v

# Push your code to GitHub
git push -u origin master
```

If you're using a different branch name (like `main`), use:
```bash
git push -u origin master:main
```

## Step 3: Verify

1. Go to https://github.com/RBadretdinov/quiz-app
2. You should see all your files there!

## Troubleshooting

### Authentication Issues

If you get authentication errors:

1. **Use Personal Access Token** (recommended):
   - Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - Generate a new token with `repo` scope
   - Use the token as your password when pushing

2. **Or use SSH**:
   - Set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
   - Use SSH URL: `git@github.com:RBadretdinov/quiz-app.git`

### Branch Name Mismatch

If GitHub uses `main` instead of `master`:
```bash
git branch -M main
git push -u origin main
```

## Next Steps After Pushing

1. **Add a README badge** (optional):
   ```markdown
   [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
   [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
   ```

2. **Enable GitHub Actions** (if you want CI/CD)

3. **Add topics/tags** to your repository for discoverability:
   - `python`
   - `fastapi`
   - `quiz-app`
   - `web-application`
   - `sqlite`

4. **Create releases** when you have stable versions

## Testing Locally

Before pushing, make sure everything works:

```bash
# Install dependencies
pip install -r requirements.txt

# Test the web app
python run_web.py

# Run tests
python -m pytest tests/
```

