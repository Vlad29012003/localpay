from .base import *
from pathlib import Path
from decouple import config as env
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOST = env('ALLOWED_HOSTS',default='localhost').split(',')


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST' , default ='db'),
        'PORT': env('POSTGRES_PORT' ,default ='5432' ,cast=int)
    }
}

TEST_MODE = 'test' in sys.argv or 'pytest' in sys.argv[0]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_TEST_DB') if TEST_MODE else env('POSTGRES_DB'),
        'USER': env('POSTGRES_TEST_USER') if TEST_MODE else env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_TEST_PASSWORD') if TEST_MODE else env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_TEST_HOST') if TEST_MODE else env('POSTGRES_HOST', default='db'),
        'PORT': env('POSTGRES_TEST_PORT') if TEST_MODE else env('POSTGRES_PORT', default='5432', cast=int)
    }
}