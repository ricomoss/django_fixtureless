from settings.base import *


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'test_django_project_db',
    'USER': 'test_user',
    'HOST': 'localhost',
    'PASSWORD': 'test_user'
}

try:
    from settings_local import *
except ImportError:
    pass
