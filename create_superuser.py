#!/usr/bin/env python
"""Script to create a Django superuser"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nayi_umeed.settings')
django.setup()

from accounts.models import User, Roles

def create_superuser():
    username = 'admin'
    email = 'admin@nayiumeed.com'
    password = 'admin123'
    phone_number = '+911234567890'
    
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists. Updating to superuser...")
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.role = Roles.ADMIN
        user.set_password(password)
        user.save()
        print(f"[OK] Updated user '{username}' to superuser")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            role=Roles.ADMIN,
            otp_verified=True
        )
        print(f"[OK] Created superuser '{username}'")
    
    print(f"\nLogin credentials:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"\nYou can now access:")
    print(f"  - Django Admin: http://127.0.0.1:8000/admin/")
    print(f"  - Custom Admin Panel: http://127.0.0.1:8000/adminpanel/")

if __name__ == '__main__':
    create_superuser()

