from __future__ import unicode_literals, absolute_import

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'internewshid'))

application = get_wsgi_application()
