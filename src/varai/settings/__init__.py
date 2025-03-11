"""
Settings initialization for varai project.
"""

import os

# Default to development settings
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'varai.settings.dev')
if settings_module != 'varai.settings.dev':
    exec(f'from {settings_module} import *') 