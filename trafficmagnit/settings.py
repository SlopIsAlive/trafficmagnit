import os
import warnings

from pathlib import Path

from __logging__ import get_logger_config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-yi5_i4u*$@y4g(iamj3(3-#u=9+&__ch1=3@0l-)(v3asq6a-e")

DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

if not DEBUG and "*" in ALLOWED_HOSTS:
    warnings.warn("ALLOWED_HOSTS contains '*' in production")


def _parse_csv_env(key: str, default: str = "") -> list[str]:
    raw = os.environ.get(key, default)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_bool_env(key: str, default: bool = False) -> bool:
    raw = os.environ.get(key, "")
    if not raw:
        return default
    return raw.lower() in ("true", "1", "yes")


def _parse_tuple_env(key: str) -> tuple[str, str] | None:
    raw = os.environ.get(key, "")
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 2:
        return (parts[0], parts[1])
    return None


CSRF_TRUSTED_ORIGINS = _parse_csv_env("CSRF_TRUSTED_ORIGINS")
SESSION_COOKIE_SECURE = _parse_bool_env("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = _parse_bool_env("CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_PROXY_SSL_HEADER = _parse_tuple_env("SECURE_PROXY_SSL_HEADER")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "django_extensions",
    "request_id",
    "django_celery_beat",
    "drf_spectacular",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "request_id.middleware.RequestIdMiddleware",
]

ROOT_URLCONF = "trafficmagnit.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "trafficmagnit.wsgi.application"


# not production code, but really useful for local development without needing to setup postgres
_DB_NAME = os.environ.get("DB_NAME") or os.environ.get("POSTGRES_DB")
_DB_USER = os.environ.get("DB_USER") or os.environ.get("POSTGRES_USER")
_DB_PASSWORD = os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
_DB_HOST = os.environ.get("DB_HOST") or os.environ.get("POSTGRES_HOST", "")
_DB_PORT = os.environ.get("DB_PORT") or os.environ.get("POSTGRES_PORT", "5432")

if _DB_NAME and _DB_USER:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _DB_NAME,
            "USER": _DB_USER,
            "PASSWORD": _DB_PASSWORD or "",
            "HOST": _DB_HOST,
            "PORT": _DB_PORT,
            "CONN_MAX_AGE": 600,
            "OPTIONS": {
                "connect_timeout": 5,
            },
        }
    }
else:
    if not DEBUG:
        raise RuntimeError("No postgres credentials found; shouldnt start in production like that")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

IS_POSTGRES = DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]

_REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# TODO remove or rethink this
if REDIS_HOST and REDIS_PORT:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 2,
                "SOCKET_TIMEOUT": 2,
                "IGNORE_EXCEPTIONS": True,
            },
            "KEY_PREFIX": "trafficmagnit",
            "TIMEOUT": 300,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "stripe_webhook": "200/minute",
    },
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    # "EXCEPTION_HANDLER": "core.exceptions.drf_exception_handler",
}

# TODO: SPECTACULAR_SETTINGS
SPECTACULAR_SETTINGS = {
    "TITLE": "Currency exchange rate",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/",
    "TAGS": [
        {"name": "", "description": ""},
    ],
}

RABBITMQ_USER = os.environ["RABBITMQ_USER"]
RABBITMQ_PASSWORD = os.environ["RABBITMQ_PASSWORD"]
RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]
RABBITMQ_PORT = os.environ["RABBITMQ_PORT"]

CELERY_BROKER_URL=f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
CELERY_RESULT_BACKEND=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TIMEZONE = TIME_ZONE

LOGGING = get_logger_config()

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
