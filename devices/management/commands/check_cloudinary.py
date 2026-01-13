"""
Management command to verify Cloudinary is configured correctly.
Run: python manage.py check_cloudinary
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary


class Command(BaseCommand):
    help = "Check if Cloudinary is properly configured"

    def handle(self, *args, **options):
        self.stdout.write("Checking Cloudinary configuration...")
        
        # Check if Cloudinary credentials are set
        cloud_name = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
        api_key = getattr(settings, "CLOUDINARY_API_KEY", "")
        api_secret = getattr(settings, "CLOUDINARY_API_SECRET", "")
        
        if not cloud_name or not api_key or not api_secret:
            self.stdout.write(self.style.ERROR("❌ Cloudinary credentials are NOT set!"))
            self.stdout.write("Please add these environment variables in Render:")
            self.stdout.write("  - CLOUDINARY_CLOUD_NAME")
            self.stdout.write("  - CLOUDINARY_API_KEY")
            self.stdout.write("  - CLOUDINARY_API_SECRET")
            return
        
        self.stdout.write(self.style.SUCCESS("✓ Cloudinary credentials found"))
        self.stdout.write(f"  Cloud Name: {cloud_name}")
        self.stdout.write(f"  API Key: {api_key[:10]}...")
        
        # Check if Cloudinary storage is enabled
        default_storage = getattr(settings, "DEFAULT_FILE_STORAGE", "")
        if "cloudinary" in default_storage.lower():
            self.stdout.write(self.style.SUCCESS("✓ Cloudinary storage is ENABLED"))
        else:
            self.stdout.write(self.style.WARNING("⚠ Cloudinary storage is NOT enabled"))
            self.stdout.write(f"  Current storage: {default_storage}")
            return
        
        # Try to connect to Cloudinary
        try:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            # Try a simple API call
            import cloudinary.api
            result = cloudinary.api.ping()
            if result.get("status") == "ok":
                self.stdout.write(self.style.SUCCESS("✓ Cloudinary connection successful!"))
                self.stdout.write("\n✅ Everything is configured correctly!")
                self.stdout.write("\nNext steps:")
                self.stdout.write("  1. Upload images via Django admin")
                self.stdout.write("  2. Images will be stored in Cloudinary automatically")
                self.stdout.write("  3. Old images need to be re-uploaded")
            else:
                self.stdout.write(self.style.ERROR("❌ Cloudinary ping failed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error connecting to Cloudinary: {str(e)}"))
            self.stdout.write("Please check your credentials in Render dashboard.")
