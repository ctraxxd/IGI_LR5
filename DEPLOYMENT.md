# 🚀 Deployment Guide - Museum Project (LR5)

This guide walks you through deploying the Museum project to Render.com.

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All tests pass: `pytest --cov=store`
- [ ] Database is populated: `python manage.py seed_data`
- [ ] Superuser exists: `python manage.py createsuperuser`
- [ ] Code is committed to Git

---

## 📦 Step 1: Create GitHub Repository

### 1.1 Initialize Git (if not already done)

```bash
cd /path/to/your/project
git init
git add .
git commit -m "Museum project - Variant 9"
```

### 1.2 Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `museum-lr5` (or any name you prefer)
3. **Visibility: Private** ⚠️ (required for grading)
4. Click "Create repository"

### 1.3 Push Code to GitHub

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/museum-lr5.git
git push -u origin main
```

---

## ☁️ Step 2: Deploy to Render.com

### 2.1 Create Render Account

1. Go to https://render.com
2. Click **Get Started for Free**
3. Sign up with GitHub (recommended) or email

### 2.2 Create New Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository (`museum-lr5`)
3. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `museum-lr5` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | (leave blank) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn config.wsgi:application` |

### 2.3 Configure Environment Variables

Click **Advanced** → **Add Environment Variable**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate random: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `DEBUG` | `False` |
| `DATABASE_URL` | (auto-filled by Render) |
| `ALLOWED_HOSTS` | `*` |

### 2.4 Database Configuration

Render will automatically:
- Create a PostgreSQL database
- Set `DATABASE_URL` environment variable
- The `render.yaml` file configures migrations

### 2.5 Deploy

1. Click **Create Web Service**
2. Wait for build (5-10 minutes)
3. Once deployed, you'll get a URL like: `https://museum-lr5.onrender.com`

---

## 🔧 Step 3: Post-Deployment

### 3.1 Run Migrations

Render runs migrations automatically via `render.yaml`. To verify:

1. Go to Render Dashboard → Your Service
2. Click **Shell** (terminal access)
3. Run: `python manage.py migrate`

### 3.2 Create Superuser

In the Render Shell:

```bash
python manage.py createsuperuser
# Enter username: admin
# Enter email: (optional)
# Enter password: (won't show)
```

### 3.3 Populate Sample Data

```bash
python manage.py seed_data
```

### 3.4 Verify Deployment

Visit:
- **Homepage:** `https://museum-lr5.onrender.com`
- **Admin:** `https://museum-lr5.onrender.com/admin`
- **Statistics:** `https://museum-lr5.onrender.com/statistics`
- **Calendar:** `https://museum-lr5.onrender.com/calendar`

---

## 📊 Step 4: Verify Coverage

Run tests locally with coverage:

```bash
source venv/bin/activate
pytest --cov=store --cov-report=html
```

Open coverage report:
```bash
open htmlcov/index.html
```

**Requirement:** 80%+ coverage

---

## 🔍 Troubleshooting

### Build Fails

**Error: `aiohttp` not found**
```bash
# Ensure requirements.txt includes:
aiohttp>=3.9.0
```

**Error: Database not found**
```bash
# Check DATABASE_URL is set in Render environment variables
# Verify render.yaml has database configuration
```

### Static Files Not Loading

Add to `config/settings.py`:

```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Then redeploy.

### 502 Bad Gateway

- Wait 2-3 minutes (Render spins down idle services)
- Check logs in Render Dashboard
- Verify `ALLOWED_HOSTS` includes your domain

---

## 📋 Submission Checklist

Before submitting:

- [ ] GitHub repository is **Private**
- [ ] Project deployed on Render.com
- [ ] Working URL submitted
- [ ] Admin credentials work
- [ ] All pages load without errors
- [ ] Statistics page shows graphs
- [ ] Calendar page works
- [ ] Tests pass with 80%+ coverage

---

## 🔗 Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Render Docs:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/
- **GitHub Student Pack:** https://education.github.com/pack

---

## 💡 Tips

1. **First Render deployment is free** but spins down after 15 min of inactivity
2. **Cold start takes 30-50 seconds** - this is normal
3. **Check logs** in Render Dashboard for debugging
4. **Keep `.env` local** - never commit secrets to Git
5. **Test locally first** before deploying

---

**Good luck with your submission! 🎓**
