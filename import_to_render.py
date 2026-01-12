"""
Script to import exported data on Render server
Run this AFTER deploying to Render and setting up PostgreSQL database.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nayi_umeed.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
from pathlib import Path
import sys

def import_data(data_file=None):
    """Import data from exported JSON file"""
    print("=" * 60)
    print("Importing Data to Render/PostgreSQL")
    print("=" * 60)
    
    # Check if data file is provided
    if not data_file:
        # Look for the export file
        data_file = Path(settings.BASE_DIR) / 'local_data_export.json'
    else:
        data_file = Path(data_file)
    
    if not data_file.exists():
        print(f"\n[ERROR] Data file not found: {data_file}")
        print("\nPlease provide the path to your exported data file:")
        print("  python import_to_render.py /path/to/local_data_export.json")
        sys.exit(1)
    
    print(f"\n[IMPORT] Importing data from: {data_file}")
    print("[WARNING] This will add data to your production database!")
    
    # Confirm
    response = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("[CANCELLED] Import cancelled.")
        sys.exit(0)
    
    try:
        print("\n[IMPORTING] Importing data...")
        print("This may take a few minutes depending on data size...\n")
        
        # Import the data
        call_command('loaddata', str(data_file), verbosity=2)
        
        print(f"\n[SUCCESS] Import completed successfully!")
        print(f"\n[NEXT STEPS]:")
        print(f"   1. Test logging in with your existing accounts")
        print(f"   2. Verify your devices, orders, and other data")
        print(f"   3. Delete the data file for security: {data_file}")
        
    except Exception as e:
        print(f"\n[ERROR] Error importing data: {e}")
        print("\nCommon issues:")
        print("  - Database connection not configured")
        print("  - Missing migrations (run: python manage.py migrate)")
        print("  - Data format mismatch")
        raise

if __name__ == '__main__':
    data_file = sys.argv[1] if len(sys.argv) > 1 else None
    import_data(data_file)
