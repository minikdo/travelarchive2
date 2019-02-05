from .base import * # noqa

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS += ['debug_toolbar', 'django_extensions']  # noqa
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa

INTERNAL_IPS = ['127.0.0.1']

# ALLOWED_HOSTS += []  # noqa

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # add STATIC_ROOT to DIRS  # noqa
]
