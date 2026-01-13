# Guide: Upload Local Images to Cloudinary

This guide will help you upload all your local device images to Cloudinary so they work on your live Render site.

## Prerequisites

1. **Cloudinary account set up** (you already have this: `duo3tqnyj`)
2. **Local images exist** in your `media/device_images/` folder
3. **Cloudinary credentials** added to your local environment

## Step 1: Set Cloudinary Credentials Locally

**Option A: Set environment variables (recommended)**

In PowerShell (Windows):
```powershell
$env:CLOUDINARY_CLOUD_NAME="duo3tqnyj"
$env:CLOUDINARY_API_KEY="436353534932931"
$env:CLOUDINARY_API_SECRET="bcuxK2hTL-UDQFyzAxnKBKbY3o8"
```

**Option B: Add to settings.py temporarily (for testing)**

Add these lines temporarily to `nayi_umeed/settings.py` before the Cloudinary config:
```python
# Temporary - remove after upload
os.environ.setdefault("CLOUDINARY_CLOUD_NAME", "duo3tqnyj")
os.environ.setdefault("CLOUDINARY_API_KEY", "436353534932931")
os.environ.setdefault("CLOUDINARY_API_SECRET", "bcuxK2hTL-UDQFyzAxnKBKbY3o8")
```

## Step 2: Run the Upload Script

Open your terminal in the project directory and run:

```powershell
python manage.py upload_images_to_cloudinary
```

**To test first (dry run):**
```powershell
python manage.py upload_images_to_cloudinary --dry-run
```

This will:
- Find all device images in your database
- Upload local images to Cloudinary
- Update database records with Cloudinary URLs
- Skip images already on Cloudinary

## Step 3: Verify Upload

After the script completes, check a few devices:
1. Go to Django admin: `http://127.0.0.1:8000/admin/devices/deviceimage/`
2. Click on a device image
3. Check the "Image" field - it should show a Cloudinary URL like:
   `https://res.cloudinary.com/duo3tqnyj/image/upload/...`

## Step 4: Export Updated Data

After images are uploaded, export your updated database:

```powershell
python export_local_data.py
```

This creates `local_data_export.json` with Cloudinary URLs.

## Step 5: Push to Render

1. **Commit and push the updated data:**
   ```powershell
   git add local_data_export.json
   git commit -m "Update data with Cloudinary image URLs"
   git push
   ```

2. **Render will automatically redeploy** and import the updated data

3. **Verify on live site:**
   - Go to `https://nayi-umeed.onrender.com/marketplace/`
   - Images should now be visible! ✅

## Troubleshooting

**"Cloudinary credentials not configured"**
- Make sure you set the environment variables (Step 1)

**"File not found locally"**
- Check that images exist in `media/device_images/` folder
- Some images might have been deleted - that's okay, they'll be skipped

**"Images still not showing on Render"**
- Make sure Cloudinary credentials are set in Render dashboard (Environment tab)
- Check Render logs for any errors
- Verify the image URLs in database point to Cloudinary (not `/media/`)

## What Happens Next?

- ✅ All images are stored permanently in Cloudinary
- ✅ Images persist across Render redeploys
- ✅ Fast CDN delivery worldwide
- ✅ Free tier: 25GB storage, 25GB bandwidth/month

---

**Note:** After successful upload, you can remove the temporary credentials from `settings.py` if you added them there.
