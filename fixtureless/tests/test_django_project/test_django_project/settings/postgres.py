from settings.base import *

import os



# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'fixtureless',
    'USER': 'fixtureless',
    'HOST': os.environ['PSQL_HOST'],
    'PASSWORD': 'fixtureless'
}

try:
    from settings_local import *
except ImportError:
    pass
