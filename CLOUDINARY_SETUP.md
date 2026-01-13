# Cloudinary Setup Guide for Image Storage

## Why Cloudinary?

Render's filesystem is **ephemeral** - any files uploaded after deployment are lost when the service restarts. Cloudinary provides permanent cloud storage for your images.

## Step 1: Create a Free Cloudinary Account

1. Go to https://cloudinary.com/users/register/free
2. Sign up with your email (free tier includes 25GB storage and 25GB bandwidth/month)
3. Verify your email

## Step 2: Get Your Cloudinary Credentials

1. After logging in, go to your **Dashboard**: https://cloudinary.com/console
2. You'll see your **Account Details** with three important values:
   - **Cloud Name** (e.g., `dxyz123abc`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz123456`)

## Step 3: Add Credentials to Render

1. Go to your Render Dashboard: https://dashboard.render.com
2. Click on your **`nayi-umeed`** web service
3. Go to the **"Environment"** tab
4. Click **"Add Environment Variable"** and add these three variables:

   ```
   CLOUDINARY_CLOUD_NAME = your_cloud_name_here
   CLOUDINARY_API_KEY = your_api_key_here
   CLOUDINARY_API_SECRET = your_api_secret_here
   ```

5. Click **"Save Changes"** - Render will automatically redeploy

## Step 4: Upload Existing Images to Cloudinary

After the redeploy completes, you need to upload your existing device images to Cloudinary. You have two options:

### Option A: Re-upload via Django Admin (Recommended)

1. Go to `https://nayi-umeed.onrender.com/admin/`
2. Log in as admin
3. Go to **Devices** → Select a device → Edit
4. Re-upload the images for each device
5. Save

### Option B: Use a Migration Script (For bulk upload)

If you have many images, I can create a script to upload all local images to Cloudinary automatically.

## Step 5: Verify Images Are Working

1. Visit `https://nayi-umeed.onrender.com/marketplace/`
2. Check if device images are displaying correctly
3. If images show up, you're all set! ✅

## Troubleshooting

- **Images still not showing?** Make sure you've added all three Cloudinary environment variables in Render
- **"Invalid credentials" error?** Double-check your Cloudinary credentials are correct
- **Need to upload many images?** Let me know and I'll create a bulk upload script

---

**Note:** The free Cloudinary tier includes:
- 25 GB storage
- 25 GB bandwidth/month
- Perfect for most small-to-medium projects!
