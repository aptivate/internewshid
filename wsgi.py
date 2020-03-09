import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'internewshid'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()
