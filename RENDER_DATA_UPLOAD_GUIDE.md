# 📤 How to Upload & Import Data on Render - Step by Step

This guide shows you exactly how to upload your `local_data_export.json` file to Render and import it into your database.

## Prerequisites

- ✅ Render deployment is complete
- ✅ Migrations have been run
- ✅ You have `local_data_export.json` file ready
- ✅ You have access to Render Shell

---

## Method 1: Using Render Shell (Recommended - Easiest)

### Step 1: Open Render Shell

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Click on your **Web Service** (nayi-umeed)
3. Click on the **"Shell"** tab at the top
4. A terminal window will open

### Step 2: Upload the File

You have **3 options** to get the file to Render:

#### Option A: Direct File Upload (Easiest)

1. In Render Shell, look for an **"Upload"** or **"File Upload"** button
2. Click it and select `local_data_export.json` from your computer
3. The file will be uploaded to Render's server

#### Option B: Using Git (Temporary)

1. **On your local computer**, temporarily add the file:
   ```bash
   git add local_data_export.json
   git commit -m "Temporary: Add data export for import"
   git push
   ```

2. **On Render**, the file will be available in your project directory

3. **After import**, remove it from git:
   ```bash
   git rm local_data_export.json
   git commit -m "Remove data export after import"
   git push
   ```

#### Option C: Copy-Paste Content (For Small Files)

1. **On your local computer**, open `local_data_export.json`
2. Copy all the content
3. **In Render Shell**, create the file:
   ```bash
   nano local_data_export.json
   ```
4. Paste the content (Right-click → Paste)
5. Press `Ctrl+X`, then `Y`, then `Enter` to save

### Step 3: Verify File is There

In Render Shell, check the file exists:
```bash
ls -la local_data_export.json
```

You should see the file listed with its size.

### Step 4: Import the Data

In Render Shell, run:
```bash
python import_to_render.py local_data_export.json
```

You'll see:
```
[IMPORT] Importing data from: local_data_export.json
[WARNING] This will add data to your production database!

Do you want to continue? (yes/no):
```

Type `yes` and press Enter.

### Step 5: Wait for Import

The import process will:
- Show progress for each model
- May take 1-2 minutes depending on data size
- Display success message when complete

### Step 6: Verify Import

Check that data was imported:
```bash
python manage.py shell
```

Then in Python shell:
```python
from accounts.models import User
from devices.models import Device
from marketplace.models import MarketplaceListing

print(f"Users: {User.objects.count()}")
print(f"Devices: {Device.objects.count()}")
print(f"Listings: {MarketplaceListing.objects.count()}")
exit()
```

### Step 7: Clean Up (Important!)

Delete the data file for security:
```bash
rm local_data_export.json
```

---

## Method 2: Using Render's File System (Alternative)

### Step 1: Access Render Shell

Same as Method 1, Step 1

### Step 2: Create File Directory

```bash
mkdir -p /tmp
cd /tmp
```

### Step 3: Upload File

Use one of the upload methods from Method 1, Step 2

### Step 4: Import from /tmp

```bash
python import_to_render.py /tmp/local_data_export.json
```

---

## Method 3: Using Render's Persistent Disk (For Large Files)

If you have a large data file, you can use Render's persistent disk:

### Step 1: Enable Persistent Disk

1. Go to your Web Service settings
2. Scroll to "Disk" section
3. Enable persistent disk (if available on your plan)

### Step 2: Upload File

Upload to the persistent disk location (usually `/persistent`)

### Step 3: Import

```bash
python import_to_render.py /persistent/local_data_export.json
```

---

## Troubleshooting

### Issue: "File not found"

**Solution**: 
- Check file path: `ls -la` to see where you are
- Use full path: `python import_to_render.py /full/path/to/local_data_export.json`
- Verify file exists: `cat local_data_export.json | head` (should show JSON)

### Issue: "Permission denied"

**Solution**:
- Make sure you're in the project directory: `cd /opt/render/project/src`
- Check file permissions: `chmod 644 local_data_export.json`

### Issue: "Database connection error"

**Solution**:
- Verify `DATABASE_URL` is set: `echo $DATABASE_URL`
- Check database is running in Render dashboard
- Run migrations first: `python manage.py migrate`

### Issue: "Import fails with duplicate key"

**Solution**:
- Database might already have data
- Clear database first (WARNING: Deletes all data):
  ```bash
  python manage.py flush
  python manage.py migrate
  python import_to_render.py local_data_export.json
  ```

### Issue: "Can't upload file in Shell"

**Solution**:
- Use Git method (Method 1, Option B)
- Or use copy-paste (Method 1, Option C)
- Or use SCP/SFTP if you have SSH access

---

## Complete Example Walkthrough

Here's a complete example of what you'll see:

```bash
# 1. Open Render Shell and navigate to project
$ cd /opt/render/project/src
$ pwd
/opt/render/project/src

# 2. Check if file exists (after upload)
$ ls -la local_data_export.json
-rw-r--r-- 1 user user 31234 Jan 13 10:30 local_data_export.json

# 3. Run import script
$ python import_to_render.py local_data_export.json

============================================================
Importing Data to Render/PostgreSQL
============================================================

[IMPORT] Importing data from: local_data_export.json
[WARNING] This will add data to your production database!

Do you want to continue? (yes/no): yes

[IMPORTING] Importing data...
This may take a few minutes depending on data size...

Installed 5 object(s) from 1 fixture(s)
Installed 11 object(s) from 1 fixture(s)
Installed 11 object(s) from 1 fixture(s)
...

[SUCCESS] Import completed successfully!

[NEXT STEPS]:
   1. Test logging in with your existing accounts
   2. Verify your devices, orders, and other data
   3. Delete the data file for security: local_data_export.json

# 4. Verify import
$ python manage.py shell
>>> from accounts.models import User
>>> User.objects.count()
5
>>> exit()

# 5. Clean up
$ rm local_data_export.json
$ ls -la local_data_export.json
ls: cannot access 'local_data_export.json': No such file or directory
```

---

## Quick Reference Commands

```bash
# Navigate to project directory
cd /opt/render/project/src

# Check file exists
ls -la local_data_export.json

# Import data
python import_to_render.py local_data_export.json

# Verify import
python manage.py shell
# Then: from accounts.models import User; print(User.objects.count())

# Delete file
rm local_data_export.json
```

---

## Security Reminder

⚠️ **IMPORTANT**: After successful import:
1. ✅ Delete `local_data_export.json` from Render
2. ✅ Delete it from your local computer (or keep encrypted)
3. ✅ Never commit it to Git (it's in `.gitignore`)
4. ✅ The file contains sensitive data (passwords, etc.)

---

## What Happens After Import?

Once imported, your Render database will have:
- ✅ All your users (can login with same passwords)
- ✅ All your devices
- ✅ All marketplace listings
- ✅ All orders
- ✅ All repair assignments
- ✅ All status history

**Your site is now fully functional with all your data!** 🎉

---

## Need Help?

If you encounter issues:
1. Check Render build/runtime logs
2. Verify file was uploaded correctly
3. Check database connection
4. Review error messages in Shell

The import script will show detailed error messages if something goes wrong.
