# Deployment & Data Persistence Guide

## Current Setup

Your project is currently using **SQLite** (`db.sqlite3`) for local development. All your data (users, devices, orders, etc.) is stored in this file on your local machine.

## Will Your Data Remain When Going Live?

### ⚠️ **Important Answer: It Depends on Your Deployment Strategy**

### Scenario 1: SQLite (Current Setup) - ❌ **NOT Recommended for Production**

If you deploy with SQLite:
- **Data will NOT persist** across different servers/devices
- SQLite is a file-based database that lives on one server
- If you deploy to a cloud service (Heroku, Railway, AWS, etc.), your local `db.sqlite3` file will NOT be automatically transferred
- **Data will be lost** unless you manually migrate it
- SQLite doesn't work well with multiple servers or high traffic

### Scenario 2: PostgreSQL (Recommended) - ✅ **Data Will Persist**

If you switch to PostgreSQL for production:
- **Data WILL persist** across all devices and servers
- PostgreSQL is a proper database server that can be hosted separately
- All users, devices, orders, etc. will be accessible from anywhere
- Multiple servers can connect to the same database
- **This is the recommended approach for production**

## How to Deploy with Data Persistence

### Option A: Migrate Local Data to Production Database

1. **Export your local data:**
   ```bash
   python manage.py dumpdata > local_data.json
   ```

2. **Deploy your application** to a hosting service (Heroku, Railway, DigitalOcean, AWS, etc.)

3. **Set up PostgreSQL** on your hosting service

4. **Import your data:**
   ```bash
   python manage.py loaddata local_data.json
   ```

### Option B: Start Fresh (Recommended for Testing)

1. Deploy with a fresh PostgreSQL database
2. Create new test accounts and data
3. This ensures a clean production environment

## Step-by-Step: Deploying with PostgreSQL

### 1. Set Up PostgreSQL Database

**Option 1: Cloud Database (Recommended)**
- **Heroku Postgres** (Free tier available)
- **Railway PostgreSQL** (Free tier available)
- **Supabase** (Free tier available)
- **AWS RDS** (Paid)
- **DigitalOcean Managed Database** (Paid)

**Option 2: Self-Hosted**
- Install PostgreSQL on your server
- Create a database and user

### 2. Update Your Settings

Your `settings.py` already supports PostgreSQL via environment variables:

```python
# This is already configured in your settings.py
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # Falls back to SQLite locally
        conn_max_age=600,
    )
}
```

### 3. Set Environment Variable

On your hosting platform, set the `DATABASE_URL` environment variable:

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### 4. Run Migrations

On your production server:
```bash
python manage.py migrate
python manage.py collectstatic
```

### 5. (Optional) Import Local Data

If you want to transfer your local data:
```bash
# On local machine
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json

# On production server
python manage.py loaddata data.json
```

## Recommended Hosting Platforms

### 1. **Railway** (Easiest for Beginners)
- ✅ Free tier available
- ✅ Automatic PostgreSQL setup
- ✅ Easy deployment from GitHub
- ✅ Automatic HTTPS

### 2. **Heroku**
- ✅ Free tier (limited)
- ✅ Add-on for PostgreSQL
- ✅ Well-documented
- ⚠️ Requires credit card for some features

### 3. **DigitalOcean App Platform**
- ✅ Simple deployment
- ✅ Managed PostgreSQL
- ⚠️ Paid (starts at $5/month)

### 4. **Render**
- ✅ Free tier available
- ✅ PostgreSQL included
- ✅ Easy setup

## Important Notes

### Media Files (Images, Documents)

Your uploaded files (device images, repair reports) are stored in the `media/` folder locally. When deploying:

1. **Use Cloud Storage** (Recommended):
   - AWS S3
   - Cloudinary
   - DigitalOcean Spaces
   - Update `MEDIA_ROOT` and `MEDIA_URL` in settings

2. **Or sync media folder** to your production server

### Static Files (CSS, JS)

Run `python manage.py collectstatic` before deployment to gather all static files.

## Quick Checklist for Deployment

- [ ] Set up PostgreSQL database (cloud or self-hosted)
- [ ] Set `DATABASE_URL` environment variable
- [ ] Set `DJANGO_SECRET_KEY` environment variable (use a strong random key)
- [ ] Set `DEBUG=False` in production
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Set up cloud storage for media files (or sync media folder)
- [ ] Run `python manage.py migrate` on production
- [ ] Run `python manage.py collectstatic` on production
- [ ] (Optional) Import local data with `loaddata`
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure backup strategy for database

## Summary

**Your current local data will NOT automatically transfer to production.** You need to:

1. **Export it manually** using `dumpdata`, OR
2. **Start fresh** with a new PostgreSQL database (recommended for testing)

**Once deployed with PostgreSQL, all data will persist and be accessible from any device** that can access your website.

## Need Help?

If you need help with:
- Setting up PostgreSQL
- Deploying to a specific platform
- Migrating your data
- Configuring environment variables

Let me know which hosting platform you're planning to use, and I can provide specific instructions!
