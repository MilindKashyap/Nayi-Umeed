# Quick Start: Deploy to Render with render.yaml

This guide uses the `render.yaml` file for automatic deployment setup.

## Prerequisites

- ✅ Render account (sign up at https://render.com)
- ✅ GitHub account
- ✅ Your code pushed to GitHub
- ✅ `local_data_export.json` file ready (from export script)

## Step 1: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Ready for Render deployment"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/nayi-umeed.git
git push -u origin main
```

## Step 2: Deploy Using render.yaml

### Option A: Automatic Setup (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +" → "Blueprint"**
3. **Connect your GitHub repository**
4. **Select the repository** containing your `render.yaml`
5. **Click "Apply"**

Render will automatically:
- ✅ Create PostgreSQL database
- ✅ Create Web Service
- ✅ Set all environment variables
- ✅ Configure build and start commands
- ✅ Connect database to web service

### Option B: Manual Setup

If you prefer manual setup, you can still use the `render.yaml` as a reference:

1. Create PostgreSQL database manually
2. Create Web Service manually
3. Copy environment variables from `render.yaml`

## Step 3: Update ALLOWED_HOSTS

After deployment, Render will give you a URL like: `https://nayi-umeed-xxxx.onrender.com`

1. **Go to your Web Service** on Render
2. **Go to "Environment" tab**
3. **Update `ALLOWED_HOSTS`** to include your actual URL:
   ```
   nayi-umeed-xxxx.onrender.com,localhost,127.0.0.1
   ```
   (Replace `xxxx` with your actual service ID)

4. **Or update `render.yaml`** and push again:
   ```yaml
   - key: ALLOWED_HOSTS
     value: nayi-umeed-xxxx.onrender.com,localhost,127.0.0.1
   ```

## Step 4: Run Migrations

1. **Go to your Web Service** on Render
2. **Click "Shell" tab**
3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

## Step 5: Import Your Data

1. **In Render Shell**, upload your `local_data_export.json` file
   - You can use the file upload feature in Render Shell
   - Or temporarily commit it to git (then remove after import)

2. **Import the data**:
   ```bash
   python import_to_render.py local_data_export.json
   ```

3. **Confirm** when prompted

4. **Delete the file** after successful import:
   ```bash
   rm local_data_export.json
   ```

## Step 6: Verify Deployment

1. **Visit your Render URL**: `https://nayi-umeed-xxxx.onrender.com`
2. **Test login** with your existing credentials
3. **Verify** your devices, orders, and data are there

## Configuration Details

### Database
- **Type**: PostgreSQL
- **Plan**: Free (change to paid for production)
- **Auto-connected** to web service via `DATABASE_URL`

### Web Service
- **Environment**: Python 3.12.4
- **Build Command**: Installs dependencies + collects static files
- **Start Command**: Gunicorn server
- **Plan**: Free (change to paid for production)

### Environment Variables (Auto-set)
- `PYTHON_VERSION`: 3.12.4
- `DJANGO_SECRET_KEY`: Auto-generated (secure)
- `DJANGO_DEBUG`: False (production mode)
- `DATABASE_URL`: Auto-connected from database
- `ALLOWED_HOSTS`: Update with your actual URL
- `TZ`: Asia/Kolkata

## Updating Plans (For Production)

To upgrade from free to paid plans, edit `render.yaml`:

```yaml
services:
  - type: pspg
    plan: starter  # or standard, pro
  - type: web
    plan: starter  # or standard, pro
```

Then push changes to trigger redeployment.

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure Python version matches

### Database Connection Errors
- Verify `DATABASE_URL` is set (should be automatic)
- Check database is running
- Verify migrations ran: `python manage.py migrate`

### Static Files Not Loading
- Check `collectstatic` ran during build
- Verify `STATIC_ROOT` is set correctly
- Check build logs for errors

### Can't Login After Import
- Verify users were imported: Check database
- Try resetting password: `python manage.py changepassword username`

## Next Steps

- ✅ Set up custom domain (optional)
- ✅ Configure email for production
- ✅ Set up automated backups
- ✅ Monitor application logs
- ✅ Set up error tracking

---

**Your site is now live!** 🎉

Visit your Render URL and login with your existing credentials!
