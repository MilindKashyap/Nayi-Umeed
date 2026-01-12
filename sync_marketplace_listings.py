"""
Script to create MarketplaceListing for all approved devices that don't have one.
Run this to sync approved devices with marketplace listings.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nayi_umeed.settings')
django.setup()

from devices.models import Device
from marketplace.models import MarketplaceListing

def sync_marketplace_listings():
    """Create MarketplaceListing for all approved devices"""
    approved_devices = Device.objects.filter(admin_approval_status="approved")
    
    print(f"Found {approved_devices.count()} approved devices")
    
    created_count = 0
    existing_count = 0
    
    for device in approved_devices:
        # Check if device already has a marketplace listing
        if hasattr(device, 'market_listing'):
            existing_count += 1
            print(f"  [OK] Device {device.listing_id} ({device.title}) already has listing")
        else:
            # Create marketplace listing
            listing_price = device.price if device.price else 0
            MarketplaceListing.objects.create(
                device=device,
                price=listing_price,
                is_active=True
            )
            created_count += 1
            print(f"  + Created listing for {device.listing_id} ({device.title}) - Price: Rs. {listing_price}")
    
    print(f"\nSummary:")
    print(f"  - Created: {created_count} new listings")
    print(f"  - Already existed: {existing_count} listings")
    print(f"  - Total approved devices: {approved_devices.count()}")
    
    # Also check marketplace listings
    all_listings = MarketplaceListing.objects.filter(is_active=True, device__admin_approval_status="approved")
    print(f"  - Active marketplace listings: {all_listings.count()}")

if __name__ == "__main__":
    sync_marketplace_listings()
