import os
import rollbar
from git import Repo

from environs import Env


env = Env()
env.read_env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

YANDEX_API_KEY = env('YANDEX_API_KEY')
ROLLBAR_TOKEN='5a33bc21da1f452984a936b9d6315aac'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', ['*'])

INSTALLED_APPS = [
    'foodcartapp.apps.FoodcartappConfig',
    'restaurateur.apps.RestaurateurConfig',
    'geoapp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
]

ROOT_URLCONF = 'star_burger.urls'

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'star_burger.wsgi.application'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('POSTGRES_DB', '{}/db.sqlite3'.format(BASE_DIR)),
        'USER': os.getenv('POSTGRES_USER', 'admin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'password'),
        'HOST': os.getenv('SQL_HOST', 'localhost'),
        'PORT': 5432,
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

INTERNAL_IPS = [
    '127.0.0.1'
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets"),
    os.path.join(BASE_DIR, "bundles"),
]

local_repo = Repo(path=BASE_DIR)
local_branch = local_repo.active_branch.name

ROLLBAR = {
    'access_token': env.str('DJANGO_ROLLBAR_TOKEN', None),
    'environment': env.str(f'ROLLBAR_ENVIRONMENT', 'undefined'),
    'branch': local_branch,
    'code_version': '1.0',
    'root': BASE_DIR,
}
