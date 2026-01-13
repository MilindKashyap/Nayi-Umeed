"""
Script to export local SQLite data for migration to Render/PostgreSQL
Automatically uploads images to Cloudinary before exporting.
Run this BEFORE deploying to Render to backup your local data.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nayi_umeed.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
import json
from pathlib import Path

def export_data():
    """Export all data from local SQLite database"""
    print("=" * 60)
    print("Exporting Local Data for Render Deployment")
    print("=" * 60)
    
    # Step 1: Upload images to Cloudinary if configured
    cloudinary_configured = (
        getattr(settings, "CLOUDINARY_CLOUD_NAME", "") and
        getattr(settings, "CLOUDINARY_API_KEY", "") and
        getattr(settings, "CLOUDINARY_API_SECRET", "")
    )
    
    if cloudinary_configured:
        print("\n[STEP 1] Cloudinary detected - uploading images...")
        try:
            call_command('upload_images_to_cloudinary', verbosity=1)
            print("[SUCCESS] Images uploaded to Cloudinary!\n")
        except Exception as e:
            print(f"[WARNING] Error uploading images to Cloudinary: {e}")
            print("[CONTINUING] Exporting data anyway (images may need manual upload)...\n")
    else:
        print("\n[SKIP] Cloudinary not configured - skipping image upload")
        print("[NOTE] Images will need to be uploaded manually or via admin after deployment\n")
    
    # Step 2: Export data
    output_file = Path(settings.BASE_DIR) / 'local_data_export.json'
    
    # Exclude some system tables that shouldn't be migrated
    excluded_models = [
        'contenttypes.contenttype',
        'sessions.session',
        'admin.logentry',
    ]
    
    try:
        print(f"\n[EXPORT] Exporting data to: {output_file}")
        print("This may take a moment...\n")
        
        # Export all data except system tables
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--exclude', 'contenttypes',
            '--exclude', 'sessions',
            '--exclude', 'admin.logentry',
            '--indent', '2',
            output=str(output_file),
        )
        
        # Get file size
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        
        print(f"[SUCCESS] Export completed successfully!")
        print(f"[FILE] File: {output_file}")
        print(f"[SIZE] Size: {file_size:.2f} MB")
        print(f"\n[EXPORTED MODELS]:")
        
        # Read and show what was exported
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            models = set()
            for item in data:
                if 'model' in item:
                    models.add(item['model'])
            
            for model in sorted(models):
                count = sum(1 for item in data if item.get('model') == model)
                print(f"   - {model}: {count} records")
        
        print(f"\n[IMPORTANT]:")
        print(f"   1. This file contains all your data with Cloudinary image URLs")
        print(f"   2. Commit and push this file to GitHub")
        print(f"   3. Render will automatically import it on next deployment")
        print(f"   4. Delete this file from GitHub after successful import (contains sensitive data)")
        
        return output_file
        
    except Exception as e:
        print(f"\n[ERROR] Error exporting data: {e}")
        raise

if __name__ == '__main__':
    export_data()
