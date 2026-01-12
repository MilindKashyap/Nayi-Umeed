"""
WSGI config for nayi_umeed project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nayi_umeed.settings")

application = get_wsgi_application()

