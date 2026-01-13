"""
Template tags for Cloudinary image URLs
TEMPORARY SOLUTION: Direct mapping of device IDs to working Cloudinary URLs
"""
from django import template

register = template.Library()

# DIRECT MAPPING - Corrected mapping based on actual device titles
# Format: "DEVICE_ID": "CLOUDINARY_URL"
DEVICE_IMAGE_URLS = {
    # Digital Thermometer
    "DEV-383B0B02": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303890/device_images/DEV-AC24891B/thermometer.jpg",
    
    # Professional Stethoscope
    "DEV-1D28C43D": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303889/device_images/DEV-3BD4155A/stethoscope.jpg",
    
    # Finger Pulse Oximeter
    "DEV-6BD3B519": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303889/device_images/DEV-8C93FAA3/pulse_oximeter.jpg",
    
    # Digital Blood Pressure Monitor
    "DEV-8C93FAA3": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303887/device_images/DEV-383B0B02/blood_pressure_monitor.jpg",
    
    # Wheelchair - Standard Model
    "DEV-3BD4155A": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768309496/WhatsApp_Image_2026-01-13_at_1.41.17_AM_orpvlc.jpg",
    
    # Patient Vital Signs Monitor
    "DEV-AC24891B": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303888/device_images/DEV-6BD3B519/patient_monitor.jpg",
    
    # ICU Ventilator Unit
    "DEV-B694C352": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303891/device_images/DEV-B694C352/ventilator%201.jpg",
    
    # Medical Ventilator System
    "DEV-B326E3D2": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303892/device_images/DEV-B326E3D2/ventilator2.jpg",
    
    # Portable Oxygen Concentrator
    "DEV-3C25EA4B": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768308483/WhatsApp_Image_2026-01-12_at_5.43.28_PM_ujxb3f.jpg",
    
    # Additional devices
    "DEV-C1E9F870": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768309496/WhatsApp_Image_2026-01-13_at_1.41.17_AM_orpvlc.jpg",  # wheelchair
    "DEV-0C22F646": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768308483/WhatsApp_Image_2026-01-12_at_5.43.28_PM_ujxb3f.jpg",  # portable oxygen concentrator
}

@register.filter
def cloudinary_url(image_field):
    """Convert image field to Cloudinary URL - uses direct mapping for immediate fix"""
    if not image_field:
        return ""
    
    try:
        # Try to get device from image_field
        # image_field is a FileField, we need to get the DeviceImage instance
        # In templates, we pass img.image, so we need to get img.device.listing_id
        # Actually, we need to pass the DeviceImage instance, not just the field
        
        # If it's already a full URL, return it
        stored_value = image_field.name if hasattr(image_field, 'name') else str(image_field)
        if "cloudinary.com" in str(stored_value) or str(stored_value).startswith("http"):
            return str(stored_value)
        
        # For now, return empty - we'll fix this in the template
        return ""
    except:
        return ""

@register.filter
def cloudinary_url_by_device(device_image):
    """Get Cloudinary URL by DeviceImage instance - uses direct mapping"""
    if not device_image:
        return ""
    
    try:
        # Get device listing_id
        device_id = device_image.device.listing_id
        
        # Check direct mapping first (TEMPORARY FIX - these are verified working URLs)
        if device_id in DEVICE_IMAGE_URLS:
            return DEVICE_IMAGE_URLS[device_id]
        
        # Fallback: try the property method
        if hasattr(device_image, 'get_image_url'):
            url = device_image.get_image_url
            if url and url.startswith('http'):
                return url
        
        # Last resort: return empty
        return ""
    except Exception as e:
        # In production, you might want to log this
        return ""
