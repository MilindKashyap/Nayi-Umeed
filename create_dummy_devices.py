"""
Script to create dummy medical devices with images for the marketplace.
This will create approved devices that will always appear in the marketplace.
"""
import os
import django
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nayi_umeed.settings')
django.setup()

from django.core.files import File
from accounts.models import User, Roles
from devices.models import Device, DeviceImage
from marketplace.models import MarketplaceListing

# Device data mapping images to device information
DEVICE_DATA = [
    {
        "image": "oxygen_concentrator.jpeg",
        "title": "Portable Oxygen Concentrator",
        "category": "oxygen_concentrator",
        "condition": "good",
        "description": "High-quality portable oxygen concentrator, fully tested and certified. Perfect for home use or travel. Includes all accessories and user manual.",
        "price": 25000.00,
    },
    {
        "image": "ventilator 1.jpeg",
        "title": "Medical Ventilator System",
        "category": "ventilator",
        "condition": "good",
        "description": "Professional-grade medical ventilator system. Recently serviced and certified. Ideal for hospital or clinic use. All safety checks completed.",
        "price": 150000.00,
    },
    {
        "image": "ventilator2 .jpeg",
        "title": "ICU Ventilator Unit",
        "category": "ventilator",
        "condition": "good",
        "description": "Advanced ICU ventilator with modern features. Fully functional and certified. Includes all necessary components and documentation.",
        "price": 180000.00,
    },
    {
        "image": "patient_monitor.jpeg",
        "title": "Patient Vital Signs Monitor",
        "category": "monitor",
        "condition": "good",
        "description": "Multi-parameter patient monitor for continuous vital signs monitoring. Display shows heart rate, blood pressure, oxygen saturation, and more. Certified and ready for use.",
        "price": 45000.00,
    },
    {
        "image": "wheelchair.jpeg",
        "title": "Wheelchair - Standard Model",
        "category": "wheelchair",
        "condition": "good",
        "description": "Comfortable and durable standard wheelchair. Lightweight frame, adjustable footrests, and smooth-rolling wheels. Excellent condition, sanitized and ready for use.",
        "price": 8000.00,
    },
    {
        "image": "blood_pressure_monitor.jpeg",
        "title": "Digital Blood Pressure Monitor",
        "category": "other",
        "condition": "new",
        "description": "Accurate digital blood pressure monitor with large display. Easy to use, includes cuff and instruction manual. Brand new, never used.",
        "price": 2500.00,
    },
    {
        "image": "pulse_oximeter.jpeg",
        "title": "Finger Pulse Oximeter",
        "category": "other",
        "condition": "new",
        "description": "Portable finger pulse oximeter for measuring blood oxygen levels and heart rate. Compact design, perfect for home monitoring. New in box.",
        "price": 1200.00,
    },
    {
        "image": "stethoscope.jpeg",
        "title": "Professional Stethoscope",
        "category": "other",
        "condition": "good",
        "description": "High-quality medical stethoscope. Excellent acoustic performance. Cleaned and sanitized. Perfect for medical professionals.",
        "price": 3500.00,
    },
    {
        "image": "thermometer.jpeg",
        "title": "Digital Thermometer",
        "category": "other",
        "condition": "new",
        "description": "Fast and accurate digital thermometer. Easy to read display, beep alert, and memory function. New, sealed package.",
        "price": 500.00,
    },
]

def create_dummy_devices():
    """Create dummy devices with images for marketplace"""
    # Get or create an admin user for device ownership
    admin_user = User.objects.filter(role=Roles.ADMIN).first()
    if not admin_user:
        # Create a dummy admin user if none exists
        admin_user = User.objects.create_user(
            username="system_admin",
            email="admin@nayiumeed.com",
            password="dummy123",
            role=Roles.ADMIN,
            phone_number="9999999999",
            otp_verified=True,
            is_staff=True,
            is_superuser=True
        )
        print(f"Created admin user: {admin_user.username}")
    
    images_dir = Path("images")
    media_dir = Path("media/device_images")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    created_count = 0
    skipped_count = 0
    
    for device_info in DEVICE_DATA:
        image_filename = device_info["image"]
        image_path = images_dir / image_filename
        
        if not image_path.exists():
            print(f"  [SKIP] Image not found: {image_filename}")
            skipped_count += 1
            continue
        
        # Check if device with this title already exists
        existing_device = Device.objects.filter(title=device_info["title"]).first()
        if existing_device:
            print(f"  [SKIP] Device already exists: {device_info['title']}")
            skipped_count += 1
            continue
        
        # Create device
        device = Device.objects.create(
            donor=admin_user,
            title=device_info["title"],
            description=device_info["description"],
            category=device_info["category"],
            condition=device_info["condition"],
            status="listed",  # Set to listed so it appears in marketplace
            admin_approval_status="approved",  # Approved by admin
            price=device_info["price"],
        )
        
        # Upload image to device
        with open(image_path, 'rb') as f:
            device_image = DeviceImage.objects.create(
                device=device,
                image=File(f, name=image_filename)
            )
        
        # Create MarketplaceListing
        MarketplaceListing.objects.create(
            device=device,
            price=device_info["price"],
            is_active=True
        )
        
        created_count += 1
        print(f"  [OK] Created: {device_info['title']} (ID: {device.listing_id}, Price: Rs. {device_info['price']})")
    
    print(f"\nSummary:")
    print(f"  - Created: {created_count} devices")
    print(f"  - Skipped: {skipped_count} devices")
    print(f"  - Total marketplace listings: {MarketplaceListing.objects.filter(device__admin_approval_status='approved', is_active=True).count()}")

if __name__ == "__main__":
    print("Creating dummy medical devices for marketplace...")
    create_dummy_devices()
    print("\nDone! Devices are now available in the marketplace.")
