# 🚀 Deployment Checklist - Nayi Umeed

## ✅ Pre-Deployment Verification

### Required Files (All Present ✓)
- [x] `requirements.txt` - Python dependencies
- [x] `Procfile` - Web server configuration
- [x] `render.yaml` - Render deployment config
- [x] `.gitignore` - Excludes sensitive files
- [x] `export_local_data.py` - Data export script
- [x] `import_to_render.py` - Data import script
- [x] `local_data_export.json` - Your exported data (keep safe!)

### Project Configuration
- [x] Django settings configured for production
- [x] PostgreSQL support via `dj-database-url`
- [x] Static files configuration
- [x] Media files configuration
- [x] Environment variables setup

## 📋 Deployment Steps

### Step 1: Final Local Checks
```bash
# Verify everything works locally
python manage.py check
python manage.py collectstatic --dry-run
```

### Step 2: Prepare Git Repository
```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Create GitHub repository, then:
git remote add origin https://github.com/yourusername/nayi-umeed.git
git push -u origin main
```

**⚠️ Important**: Make sure `local_data_export.json` is in `.gitignore` (it is!)

### Step 3: Deploy to Render

#### Option A: Using Blueprint (Automatic - Recommended)
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account
4. Select your repository: `nayi-umeed`
5. Click **"Apply"**
6. Render will automatically:
   - Create PostgreSQL database
   - Create Web Service
   - Set environment variables
   - Deploy your app

#### Option B: Manual Setup
1. Create PostgreSQL database manually
2. Create Web Service manually
3. Copy settings from `render.yaml`

### Step 4: Post-Deployment Configuration

1. **Get Your Render URL**
   - After deployment, Render gives you: `https://nayi-umeed-xxxx.onrender.com`
   - Note down the exact URL

2. **Update ALLOWED_HOSTS**
   - Go to Web Service → Environment tab
   - Update `ALLOWED_HOSTS` with your actual URL:
     ```
     nayi-umeed-xxxx.onrender.com,localhost,127.0.0.1
     ```
   - Or update `render.yaml` and push again

3. **Run Migrations**
   - Go to Web Service → Shell tab
   - Run:
     ```bash
     python manage.py migrate
     ```

4. **Create Superuser** (Optional)
   ```bash
   python manage.py createsuperuser
   ```

### Step 5: Import Your Data

1. **Upload Data File**
   - In Render Shell, upload `local_data_export.json`
   - Or temporarily commit to git (remove after import)

2. **Import Data**
   ```bash
   python import_to_render.py local_data_export.json
   ```
   - Type `yes` when prompted

3. **Verify Import**
   - Check that users, devices, orders are imported
   - Count records if needed

4. **Delete Data File** (Security)
   ```bash
   rm local_data_export.json
   ```

### Step 6: Verify Deployment

- [ ] Visit your Render URL
- [ ] Test login with existing credentials
- [ ] Verify devices are visible
- [ ] Check marketplace listings
- [ ] Test order placement
- [ ] Verify admin panel access
- [ ] Check static files loading
- [ ] Test image uploads (if applicable)

## 🔒 Security Checklist

- [ ] `DEBUG=False` in production (set in render.yaml)
- [ ] `DJANGO_SECRET_KEY` is auto-generated (secure)
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] Data export file deleted after import
- [ ] `.gitignore` excludes sensitive files
- [ ] HTTPS enabled (Render does this automatically)

## 📊 Post-Deployment Tasks

### Immediate
- [ ] Test all major features
- [ ] Verify data integrity
- [ ] Check error logs
- [ ] Test user registration/login

### Short-term
- [ ] Set up custom domain (optional)
- [ ] Configure email settings
- [ ] Set up monitoring
- [ ] Configure backups

### Long-term
- [ ] Upgrade to paid plan (if needed)
- [ ] Set up CI/CD
- [ ] Configure error tracking (Sentry)
- [ ] Set up analytics

## 🆘 Troubleshooting

### Build Fails
- Check build logs in Render
- Verify `requirements.txt` is correct
- Ensure Python version matches

### Database Connection Error
- Verify `DATABASE_URL` is set
- Check database is running
- Run migrations: `python manage.py migrate`

### Static Files Not Loading
- Check `collectstatic` ran during build
- Verify `STATIC_ROOT` in settings
- Check build logs

### Can't Login
- Verify users were imported
- Check database: `python manage.py shell` → `from accounts.models import User; User.objects.all()`
- Reset password: `python manage.py changepassword username`

### 500 Internal Server Error
- Check runtime logs in Render
- Temporarily set `DJANGO_DEBUG=True` to see errors
- Check `ALLOWED_HOSTS` is correct

## 📝 Important Notes

1. **Free Tier Limitations**:
   - Services spin down after 15 min inactivity
   - First request after spin-down takes ~30 seconds
   - Consider paid plan for production

2. **Media Files**:
   - Currently stored on Render disk (temporary)
   - For production, use cloud storage (S3, Cloudinary)

3. **Database Backups**:
   - Free tier: Manual backups only
   - Paid tier: Automatic backups
   - Export data regularly: `python manage.py dumpdata > backup.json`

4. **Updates**:
   - Push to GitHub → Auto-deploys
   - Or manually trigger redeploy in Render

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ Site loads at Render URL
- ✅ Can login with existing credentials
- ✅ All data is visible and accessible
- ✅ No errors in logs
- ✅ Static files load correctly
- ✅ Forms and features work

---

## Quick Reference

**Render Dashboard**: https://dashboard.render.com  
**Your App URL**: `https://nayi-umeed-xxxx.onrender.com` (after deployment)  
**Data Export File**: `local_data_export.json` (keep safe until imported)  
**Import Script**: `python import_to_render.py local_data_export.json`

---

**You're ready to deploy! 🚀**

Follow the steps above, and your site will be live with all your data accessible from anywhere!
