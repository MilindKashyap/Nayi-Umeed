"""
Script to export local SQLite data for migration to Render/PostgreSQL
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
        print(f"   1. Keep this file safe - it contains all your data")
        print(f"   2. Upload this file to Render after deployment")
        print(f"   3. Run the import script on Render to load this data")
        print(f"   4. Delete this file after successful import (contains sensitive data)")
        
        return output_file
        
    except Exception as e:
        print(f"\n[ERROR] Error exporting data: {e}")
        raise

if __name__ == '__main__':
    export_data()
