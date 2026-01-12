# Deploying to Render with Data Migration

This guide will help you deploy your Nayi Umeed project to Render and transfer your existing local data.

## Prerequisites

- ✅ Render account (sign up at https://render.com - free tier available)
- ✅ GitHub account (to connect your repository)
- ✅ Your local data exported (we'll do this)

## Step 1: Export Your Local Data

**Before deploying**, export your local SQLite data:

```bash
# Make sure you're in the project directory
cd "C:\Users\Dell\OneDrive\Desktop\NAYI UMEED"

# Activate virtual environment
.\.venv_local\Scripts\Activate.ps1

# Run the export script
python export_local_data.py
```

This will create a file called `local_data_export.json` containing all your:
- Users (with passwords - they'll work on Render!)
- Devices
- Marketplace listings
- Repair assignments
- Orders
- All other data

**Keep this file safe!** You'll need it after deployment.

## Step 2: Prepare Your Repository

### 2.1 Create a `.gitignore` (if not exists)

Make sure `.gitignore` includes:
```
*.pyc
__pycache__/
db.sqlite3
local_data_export.json  # Don't commit your data!
.env
.venv*/
venv/
*.log
media/
staticfiles/
```

### 2.2 Create `render.yaml` (Optional but Recommended)

Create a file called `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: nayi-umeed
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
    startCommand: gunicorn nayi_umeed.wsgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.4
      - key: DJANGO_SETTINGS_MODULE
        value: nayi_umeed.settings
      - key: DJANGO_SECRET_KEY
        generateValue: true
      - key: DJANGO_DEBUG
        value: False
      - key: DATABASE_URL
        fromDatabase:
          name: nayi-umeed-db
          property: connectionString
      - key: ALLOWED_HOSTS
        value: your-app-name.onrender.com

databases:
  - name: nayi-umeed-db
    databaseName: nayi_umeed
    user: nayi_umeed_user
    plan: free  # or paid plan for production
```

### 2.3 Create `requirements.txt` (if not exists)

Make sure you have all dependencies:

```bash
pip freeze > requirements.txt
```

Important packages should include:
- Django
- django-rest-framework
- dj-database-url
- psycopg2-binary (for PostgreSQL)
- gunicorn (for production server)
- Pillow (for image handling)

### 2.4 Create `Procfile` (for Render)

Create a file called `Procfile` (no extension):

```
web: gunicorn nayi_umeed.wsgi:application
```

## Step 3: Deploy to Render

### 3.1 Push to GitHub

1. Initialize git (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Render deployment"
   ```

2. Create a GitHub repository and push:
   ```bash
   git remote add origin https://github.com/yourusername/nayi-umeed.git
   git push -u origin main
   ```

### 3.2 Create Render Services

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `nayi-umeed-db`
   - Plan: Free (or paid)
   - Region: Choose closest to you
   - Click "Create Database"
   - **Copy the Internal Database URL** (you'll need this)

3. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name**: `nayi-umeed` (or your choice)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
     - **Start Command**: `gunicorn nayi_umeed.wsgi:application`
     - **Plan**: Free (or paid)

4. **Set Environment Variables**:
   In the Web Service settings, go to "Environment" and add:
   
   ```
   DATABASE_URL = <paste the Internal Database URL from PostgreSQL>
   DJANGO_SECRET_KEY = <generate a strong random key>
   DJANGO_DEBUG = False
   ALLOWED_HOSTS = your-app-name.onrender.com
   PYTHON_VERSION = 3.12.4
   ```
   
   To generate a secret key:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Wait for deployment to complete (5-10 minutes)

## Step 4: Run Migrations on Render

After deployment, you need to run migrations:

1. **Open Render Shell**:
   - Go to your Web Service on Render
   - Click "Shell" tab
   - This opens a terminal

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create superuser** (optional, if you want a new admin):
   ```bash
   python manage.py createsuperuser
   ```

## Step 5: Import Your Local Data

### 5.1 Upload Data File to Render

You have two options:

**Option A: Using Render Shell (Recommended)**

1. Open Render Shell (from your Web Service)
2. Upload the file:
   ```bash
   # In Render Shell, create a temporary directory
   mkdir -p /tmp
   ```
   
3. **From your local machine**, use Render's file upload or:
   - Go to Render Dashboard → Your Web Service → "Shell"
   - Use the file upload feature, OR
   - Copy the contents of `local_data_export.json` and paste into a file on Render

**Option B: Using Git (Alternative)**

1. Temporarily add the file to git (for one commit only):
   ```bash
   git add local_data_export.json
   git commit -m "Temporary: Add data export"
   git push
   ```
   
2. After import, remove it:
   ```bash
   git rm local_data_export.json
   git commit -m "Remove data export"
   git push
   ```

### 5.2 Import the Data

1. **In Render Shell**, run:
   ```bash
   python import_to_render.py local_data_export.json
   ```
   
   Or if the file is in a different location:
   ```bash
   python import_to_render.py /path/to/local_data_export.json
   ```

2. **Confirm the import** when prompted

3. Wait for import to complete (may take a few minutes)

## Step 6: Verify and Clean Up

1. **Test your deployment**:
   - Visit: `https://your-app-name.onrender.com`
   - Try logging in with your existing credentials
   - Verify your devices, orders, etc. are there

2. **Delete the data file** (for security):
   ```bash
   # In Render Shell
   rm local_data_export.json
   ```

3. **Remove from git** (if you committed it):
   ```bash
   git rm local_data_export.json
   git commit -m "Remove data export after import"
   git push
   ```

## Step 7: Set Up Media Files (Images, Documents)

Your uploaded files (device images, repair reports) need special handling:

### Option A: Use Cloud Storage (Recommended)

1. **Set up AWS S3, Cloudinary, or similar**
2. **Install django-storages**:
   ```bash
   pip install django-storages boto3
   ```
3. **Update settings.py** to use cloud storage
4. **Re-upload media files** or sync them

### Option B: Use Render Disk (Temporary)

Render provides persistent disk storage, but it's not ideal for production.

## Troubleshooting

### Issue: Import fails with "duplicate key" errors
**Solution**: Your database might already have some data. Clear it first:
```bash
python manage.py flush  # WARNING: Deletes all data!
python manage.py migrate
python import_to_render.py local_data_export.json
```

### Issue: Can't login after import
**Solution**: User passwords are hashed and should work. If not:
1. Check if users were imported: `python manage.py shell` → `from accounts.models import User; print(User.objects.count())`
2. Reset password: `python manage.py changepassword username`

### Issue: Static files not loading
**Solution**: Make sure `collectstatic` ran during build. Check Render build logs.

### Issue: Database connection errors
**Solution**: 
1. Verify `DATABASE_URL` is set correctly
2. Check PostgreSQL is running
3. Verify the connection string format

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] Data export file deleted after import
- [ ] HTTPS enabled (Render does this automatically)
- [ ] Database credentials secure (Render handles this)

## Next Steps

1. ✅ Set up custom domain (optional)
2. ✅ Configure email settings for production
3. ✅ Set up automated backups
4. ✅ Monitor application logs
5. ✅ Set up error tracking (Sentry, etc.)

## Need Help?

If you encounter issues:
1. Check Render build logs
2. Check Render runtime logs
3. Use Render Shell to debug
4. Check Django error pages (if DEBUG=True temporarily)

---

**Your data will now be accessible from anywhere!** 🎉

Once deployed, you can:
- Login with your existing credentials
- Access all your devices and data
- Share the site with others
- Use it from any device
