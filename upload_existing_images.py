"""
Script to upload images from local images folder to Cloudinary and update database.
Run: python upload_existing_images.py
"""
import os
import django
from pathlib import Path

# Set Cloudinary credentials BEFORE Django setup
os.environ['CLOUDINARY_CLOUD_NAME'] = 'duo3tqnyj'
os.environ['CLOUDINARY_API_KEY'] = '436353534932931'
os.environ['CLOUDINARY_API_SECRET'] = 'bcuxK2hTL-UDQFyzAxnKBKbY3o8'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nayi_umeed.settings')
django.setup()

from django.core.files.base import ContentFile
from devices.models import Device, DeviceImage
import cloudinary
import cloudinary.uploader

# Set Cloudinary credentials
cloudinary.config(
    cloud_name="duo3tqnyj",
    api_key="436353534932931",
    api_secret="bcuxK2hTL-UDQFyzAxnKBKbY3o8",
    secure=True
)

def upload_images():
    """Upload images from local images folder to Cloudinary"""
    print("=" * 60)
    print("Uploading Images to Cloudinary")
    print("=" * 60)
    
    # Check for images folder
    images_dir = Path("images")
    if not images_dir.exists():
        print(f"\n[ERROR] Images folder not found: {images_dir}")
        print("Please create an 'images' folder and put your device images there.")
        return
    
    # Get all image files
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png"))
    
    if not image_files:
        print(f"\n[ERROR] No image files found in {images_dir}")
        print("Supported formats: .jpg, .jpeg, .png")
        return
    
    print(f"\n[FOUND] {len(image_files)} image file(s) in images folder")
    
    # Get all devices that need images
    devices = Device.objects.all()
    print(f"[FOUND] {devices.count()} device(s) in database\n")
    
    uploaded = 0
    skipped = 0
    
    for device in devices:
        # Check if device already has images on Cloudinary
        existing_images = device.images.all()
        has_cloudinary = False
        for img in existing_images:
            if "cloudinary.com" in img.image.url:
                has_cloudinary = True
                break
        
        if has_cloudinary:
            print(f"[SKIP] Device {device.listing_id} already has Cloudinary images")
            skipped += 1
            continue
        
        # Try to find matching image file
        # Look for files that might match the device title or listing_id
        matching_file = None
        for img_file in image_files:
            filename_lower = img_file.name.lower()
            device_title_lower = device.title.lower().replace(" ", "_")
            
            # Try to match by device title keywords
            if any(keyword in filename_lower for keyword in device_title_lower.split() if len(keyword) > 3):
                matching_file = img_file
                break
        
        # If no match found, use first available image
        if not matching_file and image_files:
            matching_file = image_files[0]
        
        if matching_file:
            try:
                print(f"[UPLOAD] Uploading {matching_file.name} for device {device.listing_id}...")
                
                # Read file
                with open(matching_file, 'rb') as f:
                    file_data = f.read()
                
                # Delete old images if any
                device.images.all().delete()
                
                # Upload directly to Cloudinary first
                # Clean filename (remove trailing spaces)
                clean_filename = matching_file.stem.strip()
                public_id = f"device_images/{device.listing_id}/{clean_filename}"
                upload_result = cloudinary.uploader.upload(
                    file_data,
                    public_id=public_id,
                    resource_type="image"
                )
                cloudinary_url = upload_result['secure_url']
                
                # Now create DeviceImage with Cloudinary URL
                # We'll save the Cloudinary URL directly
                device_image = DeviceImage.objects.create(device=device)
                device_image.image.name = upload_result['public_id']
                device_image.save()
                
                print(f"  [OK] Uploaded to Cloudinary: {cloudinary_url}")
                uploaded += 1
                
                # Remove used file from list
                image_files.remove(matching_file)
                
            except Exception as e:
                print(f"  [ERROR] Failed to upload: {str(e)}")
        else:
            print(f"[SKIP] No image file found for device {device.listing_id}")
            skipped += 1
    
    print("\n" + "=" * 60)
    print("Upload Summary:")
    print(f"  [OK] Uploaded: {uploaded}")
    print(f"  [SKIP] Skipped: {skipped}")
    print("=" * 60)
    
    if uploaded > 0:
        print("\n[SUCCESS] Images uploaded to Cloudinary!")
        print("\nNext steps:")
        print("  1. Export updated data: python export_local_data.py")
        print("  2. Push to GitHub: git add local_data_export.json && git commit -m 'Update with Cloudinary images' && git push")
        print("  3. Render will automatically import the updated data")

if __name__ == '__main__':
    upload_images()
