import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'ui/static'),
]

# List of finder classes that know how to find static files in various locations
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Ensure 'django.contrib.staticfiles' is in INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps ...
    'django.contrib.staticfiles',
    # ... your apps ...
] 