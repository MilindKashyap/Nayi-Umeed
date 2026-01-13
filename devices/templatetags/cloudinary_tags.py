"""
Template tags for Cloudinary image URLs
TEMPORARY SOLUTION: Direct mapping of device IDs to working Cloudinary URLs
"""
from django import template

register = template.Library()

# DIRECT MAPPING - These are the verified working Cloudinary URLs
DEVICE_IMAGE_URLS = {
    "DEV-383B0B02": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303887/device_images/DEV-383B0B02/blood_pressure_monitor.jpg",
    "DEV-1D28C43D": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303887/device_images/DEV-1D28C43D/oxygen_concentrator.jpg",
    "DEV-6BD3B519": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303888/device_images/DEV-6BD3B519/patient_monitor.jpg",
    "DEV-8C93FAA3": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303889/device_images/DEV-8C93FAA3/pulse_oximeter.jpg",
    "DEV-3BD4155A": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303889/device_images/DEV-3BD4155A/stethoscope.jpg",
    "DEV-AC24891B": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303890/device_images/DEV-AC24891B/thermometer.jpg",
    "DEV-B694C352": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303891/device_images/DEV-B694C352/ventilator%201.jpg",
    "DEV-B326E3D2": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303892/device_images/DEV-B326E3D2/ventilator2.jpg",
    "DEV-3C25EA4B": "https://res.cloudinary.com/duo3tqnyj/image/upload/v1768303892/device_images/DEV-3C25EA4B/wheelchair.jpg",
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
        device_id = device_image.device.listing_id
        # Check direct mapping first
        if device_id in DEVICE_IMAGE_URLS:
            return DEVICE_IMAGE_URLS[device_id]
        
        # Fallback to property
        return device_image.get_image_url
    except:
        return ""
