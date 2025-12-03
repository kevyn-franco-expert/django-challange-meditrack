from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-dev-key-change-in-production'
)

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv()
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.core',
    'apps.patients',
    'apps.records',
    'apps.audit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.ClientTypeMiddleware',
    'apps.audit.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator'
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_VERSIONING_CLASS': (
        'rest_framework.versioning.AcceptHeaderVersioning'
    ),
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2', 'v3'],
    'VERSION_PARAM': 'version',
}

CLIENT_TYPES = {
    'LEGACY_HOSPITAL': 'legacy_hospital',
    'MODERN_CLINIC': 'modern_clinic',
    'MOBILE_APP': 'mobile_app',
}

CLIENT_FIELD_CONFIGS = {
    'legacy_hospital': {
        'required_fields': [
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'phone'
        ],
        'audit_enabled': False,
        'rate_limit': 1000,
        'allow_field_selection': False,
    },
    'modern_clinic': {
        'required_fields': ['email'],
        'audit_enabled': False,
        'rate_limit': 5000,
        'allow_field_selection': True,
    },
    'mobile_app': {
        'required_fields': ['email'],
        'audit_enabled': False,
        'rate_limit': 10000,
        'allow_field_selection': True,
    }
}

AUDIT_ENABLED_CLIENTS = config(
    'AUDIT_ENABLED_CLIENTS',
    default='premium_clinic_1,premium_clinic_2',
    cast=Csv()
)