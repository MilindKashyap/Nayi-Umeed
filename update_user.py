#!/usr/bin/env python
"""Script to update existing user to superuser"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nayi_umeed.settings')
django.setup()

from accounts.models import User, Roles

username = 'ShaliniMaam'

if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    user.is_staff = True
    user.is_superuser = True
    user.role = Roles.ADMIN
    user.save()
    print(f"[OK] Updated '{username}' to superuser with ADMIN role")
    print(f"User can now access Django Admin at /admin/")
else:
    print(f"User '{username}' not found")

