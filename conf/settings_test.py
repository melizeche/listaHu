"""
Self-contained settings used to run the test suite.

The regular ``conf/settings.py`` is deliberately not tracked by git (it holds
the secret key and the database credentials), so the tests ship with their own
settings module instead of importing it.  Run the suite with::

    ./manage.py test --settings=conf.settings_test

SQLite is used by default so the suite runs without any external service.  A
handful of views rely on PostgreSQL-only features (``DISTINCT ON``); the tests
covering those are skipped automatically unless the suite runs against
PostgreSQL, which can be requested with::

    LISTAHU_TEST_DB=postgres ./manage.py test --settings=conf.settings_test
"""

import os
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = "listahu-insecure-key-only-used-by-the-test-suite"

DEBUG = False

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "backend",
    "rest_framework",
    "corsheaders",
)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

# The models predate the setting, so keep the implicit AutoField primary keys
# instead of migrating every table to BigAutoField.
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ROOT_URLCONF = "conf.urls"

WSGI_APPLICATION = "conf.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

if os.environ.get("LISTAHU_TEST_DB") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("LISTAHU_TEST_DB_NAME", "listahu"),
            "USER": os.environ.get("LISTAHU_TEST_DB_USER", "postgres"),
            "PASSWORD": os.environ.get("LISTAHU_TEST_DB_PASSWORD", ""),
            "HOST": os.environ.get("LISTAHU_TEST_DB_HOST", "localhost"),
            "PORT": os.environ.get("LISTAHU_TEST_DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
    }

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Asuncion"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# Uploads created by the tests go to a throwaway directory so the working copy
# is never polluted with fixture screenshots.
# NOTE: the trailing separator matters -- ``backend.models.thumbnail``
# builds the thumbnail path with ``settings.MEDIA_ROOT + str(...)``.
MEDIA_ROOT = tempfile.mkdtemp(prefix="listahu-test-media-") + os.sep
MEDIA_URL = "/media/"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_URLS_REGEX = r"/api/v1/denuncias.*$"
CORS_ALLOW_METHODS = ("GET",)

# Keep the suite fast: the hashing algorithm is irrelevant to what is tested.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
