"""
ASGI config for nayi_umeed project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nayi_umeed.settings")

application = get_asgi_application()

