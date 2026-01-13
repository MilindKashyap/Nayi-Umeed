"""
Management command to upload all local device images to Cloudinary.
Run locally: python manage.py upload_images_to_cloudinary

This will:
1. Find all DeviceImage objects with local file paths
2. Upload each image to Cloudinary
3. Update the database record to use Cloudinary URL
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
import cloudinary
import cloudinary.uploader
from devices.models import DeviceImage


class Command(BaseCommand):
    help = "Upload all local device images to Cloudinary"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Check Cloudinary configuration
        cloud_name = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
        api_key = getattr(settings, "CLOUDINARY_API_KEY", "")
        api_secret = getattr(settings, "CLOUDINARY_API_SECRET", "")
        
        if not cloud_name or not api_key or not api_secret:
            self.stdout.write(self.style.ERROR("❌ Cloudinary credentials not configured!"))
            self.stdout.write("Please set these environment variables:")
            self.stdout.write("  - CLOUDINARY_CLOUD_NAME")
            self.stdout.write("  - CLOUDINARY_API_KEY")
            self.stdout.write("  - CLOUDINARY_API_SECRET")
            return
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        self.stdout.write(self.style.SUCCESS("✓ Cloudinary configured"))
        self.stdout.write(f"  Cloud Name: {cloud_name}\n")
        
        # Get all device images
        device_images = DeviceImage.objects.all()
        total = device_images.count()
        
        if total == 0:
            self.stdout.write("No device images found in database.")
            return
        
        self.stdout.write(f"Found {total} device image(s) to process...\n")
        
        uploaded_count = 0
        skipped_count = 0
        error_count = 0
        
        for img in device_images:
            try:
                # Check if image already has Cloudinary URL
                image_url = img.image.url
                if "cloudinary.com" in image_url:
                    self.stdout.write(f"⏭ Skipping {img} - already on Cloudinary")
                    skipped_count += 1
                    continue
                
                # Get the local file path
                if not img.image:
                    self.stdout.write(self.style.WARNING(f"⚠ Skipping {img} - no image file"))
                    skipped_count += 1
                    continue
                
                # Check if local file exists
                local_path = img.image.path if hasattr(img.image, 'path') else None
                if local_path and os.path.exists(local_path):
                    if dry_run:
                        self.stdout.write(f"[DRY RUN] Would upload: {img} -> {local_path}")
                        uploaded_count += 1
                        continue
                    
                    # Read the file
                    with open(local_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Create public_id based on device listing_id and filename
                    filename = os.path.basename(local_path)
                    public_id = f"device_images/{img.device.listing_id}/{filename.rsplit('.', 1)[0]}"
                    
                    # Upload to Cloudinary using Django's file handling
                    # This will automatically use Cloudinary storage if configured
                    self.stdout.write(f"📤 Uploading {img}...")
                    
                    # Read file and save through Django, which will upload to Cloudinary
                    with open(local_path, 'rb') as f:
                        img.image.save(
                            filename,
                            ContentFile(f.read()),
                            save=True
                        )
                    
                    # Get the Cloudinary URL
                    cloudinary_url = img.image.url
                    
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Uploaded: {cloudinary_url}"))
                    uploaded_count += 1
                    
                else:
                    # File doesn't exist locally - might already be on Cloudinary or missing
                    if "cloudinary.com" not in image_url:
                        self.stdout.write(self.style.WARNING(f"⚠ File not found locally: {img}"))
                        error_count += 1
                    else:
                        skipped_count += 1
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error processing {img}: {str(e)}"))
                error_count += 1
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("Upload Summary:"))
        self.stdout.write(f"  ✓ Uploaded: {uploaded_count}")
        self.stdout.write(f"  ⏭ Skipped: {skipped_count}")
        self.stdout.write(f"  ❌ Errors: {error_count}")
        self.stdout.write(f"  Total: {total}")
        
        if uploaded_count > 0 and not dry_run:
            self.stdout.write("\n✅ Images uploaded successfully!")
            self.stdout.write("\nNext steps:")
            self.stdout.write("  1. Export your updated database: python manage.py dumpdata > updated_data.json")
            self.stdout.write("  2. Import to Render (or let startup.sh handle it)")
