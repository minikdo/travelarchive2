from .base import * # noqa

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': get_secret('DB_ENGINE'),
        'NAME': get_secret('DB_NAME'),
        'USER': get_secret('DB_USER'),
        'HOST': get_secret('DB_HOST'),
        'PORT': get_secret('DB_PORT'),
    }
}

ALLOWED_HOSTS += ['10.4.0.1', 'travelarchive2']

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
