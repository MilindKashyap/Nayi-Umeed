"""
Template tags for Cloudinary image URLs
"""
from django import template

register = template.Library()

@register.filter
def cloudinary_url(image_field):
    """Convert image field to Cloudinary URL"""
    if not image_field:
        return ""
    
    cloud_name = "duo3tqnyj"
    
    try:
        stored_value = image_field.name if hasattr(image_field, 'name') else str(image_field)
        
        if not stored_value:
            return ""
        
        stored_value = str(stored_value)
        
        # If already a full URL, return it
        if "cloudinary.com" in stored_value or stored_value.startswith("http"):
            return stored_value
        
        # Clean paths
        if "nayi_umeed/device_images/nayi_umeed/device_images" in stored_value:
            stored_value = stored_value.replace("nayi_umeed/device_images/nayi_umeed/device_images/", "device_images/")
        
        if stored_value.startswith("/media/"):
            stored_value = stored_value.replace("/media/", "")
        
        # Known versions for verified images
        known_versions = {
            "device_images/DEV-383B0B02/blood_pressure_monitor": "v1768303887",
            "device_images/DEV-1D28C43D/oxygen_concentrator": "v1768303887",
            "device_images/DEV-6BD3B519/patient_monitor": "v1768303888",
            "device_images/DEV-8C93FAA3/pulse_oximeter": "v1768303889",
            "device_images/DEV-3BD4155A/stethoscope": "v1768303889",
            "device_images/DEV-AC24891B/thermometer": "v1768303890",
            "device_images/DEV-B694C352/ventilator 1": "v1768303891",
            "device_images/DEV-B326E3D2/ventilator2": "v1768303892",
            "device_images/DEV-3C25EA4B/wheelchair": "v1768303892",
        }
        
        version = known_versions.get(stored_value, "v1")
        
        if '.' not in stored_value.split('/')[-1]:
            stored_value = f"{stored_value}.jpg"
        
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{version}/{stored_value}"
    except:
        return ""
