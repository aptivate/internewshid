#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'internewshid'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
