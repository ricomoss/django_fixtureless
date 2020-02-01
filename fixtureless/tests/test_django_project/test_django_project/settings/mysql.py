import os

from settings.base import *


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'fixtureless',
    'USER': 'fixtureless',
    'PASSWORD': 'fixtureless',
    'HOST': os.environ['MYSQL_HOST'],
    'TEST': {
        'NAME': 'fixtureless',
    }
}

try:
    from settings_local import *
except ImportError:
    pass
