import os
from pathlib import Path

if os.path.isfile("env.py"):
    import env

import dj_database_url
from django.contrib.messages import constants as messages
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = "DEVELOPMENT" in os.environ

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        (
            "tarh-tastyhub-4071346c00af.herokuapp.com,"
            "localhost,127.0.0.1"
        ),
    ).split(",")
    if host.strip()
]

SECRET_KEY = os.environ.get("SECRET_KEY")

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in (
        "localhost", "127.0.0.1"
    )
]

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "django_htmx_messages",
    "crispy_forms",
    "crispy_bootstrap5",
    "storages",
    "home",
    "dishes",
    "bag",
    "checkout",
    "profiles",
    "feedback",
]

CRISPY_TEMPLATE_PACK = "bootstrap5"

SITE_ID = 1

ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Tarh Tastyhub]"
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "username*",
    "password1*",
    "password2*",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

MESSAGE_TAGS = {
    messages.DEBUG: "alert alert-secondary",
    messages.INFO: "alert alert-info",
    messages.SUCCESS: "alert alert-success",
    messages.WARNING: "alert alert-warning",
    messages.ERROR: "alert alert-danger",
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Near the top of the list so it runs last on the way out and
    # compresses the final response body (HTML/JSON) before it's sent -
    # nothing here compressed responses before, and Heroku's router
    # doesn't do it for you.
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_htmx_messages.middleware.HtmxMessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "tarh_tastyhub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "templates" / "allauth",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bag.context_processors.bag_contents",
                "dishes.context_processors.menu_dishes",
                "dishes.context_processors.categories_nav",
                "tarh_tastyhub.context_processors.static_origin",
            ],
            "builtins": [
                "crispy_forms.templatetags.crispy_forms_tags",
                "crispy_forms.templatetags.crispy_forms_field",
            ],
        },
    },
]

WSGI_APPLICATION = "tarh_tastyhub.wsgi.application"

if "DATABASE_URL" in os.environ:
    DATABASES = {
        "default": dj_database_url.parse(
            os.environ.get("DATABASE_URL"),
            # Without this, Django opens a brand-new TCP+TLS connection
            # to Postgres on every single request (default conn_max_age=0),
            # which is a big chunk of the checkout page's slow TTFB.
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

USE_AWS = os.environ.get("USE_AWS") == "True"

if USE_AWS:
    AWS_QUERYSTRING_AUTH = False
    # Cache-Control is set per-file via object_parameters on the storage
    # classes in custom_storages.py - the S3Boto3Storage backend used here
    # doesn't read AWS_HEADERS at all, so that legacy (boto2-era) setting
    # was a no-op.
    # Gzip-compress CSS/JS/SVG on upload and set Content-Encoding: gzip -
    # nothing serves compressed static assets otherwise, since S3 doesn't
    # compress on the fly the way a typical web server does.
    AWS_IS_GZIPPED = True

    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get(
        "AWS_STORAGE_BUCKET_NAME"
    )
    AWS_S3_REGION_NAME = os.environ.get(
        "AWS_S3_REGION_NAME"
    )

    # CLOUDFRONT_DOMAIN is optional: once a CloudFront distribution is put
    # in front of the bucket (see DEPLOYMENT.md), set it in Heroku config
    # vars to serve static/media over HTTP/2 instead of straight from S3
    # (which only speaks HTTP/1.1). Falls back to the raw S3 domain.
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("CLOUDFRONT_DOMAIN") or (
        f"{AWS_STORAGE_BUCKET_NAME}."
        f"s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    )

    STATICFILES_STORAGE = (
        "custom_storages.StaticManifestStorage"
    )
    DEFAULT_FILE_STORAGE = "custom_storages.MediaStorage"

    STATIC_URL = (
        f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    )
    MEDIA_URL = (
        f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    )

if not USE_AWS:
    STATIC_URL = "/static/"
    STATICFILES_DIRS = [BASE_DIR / "static"]

FREE_DELIVERY_THRESHOLD = Decimal("60.00")
DEFAULT_DELIVERY_FEE = Decimal("4.00")

STRIPE_CURRENCY = "usd"
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WH_SECRET")

DEFAULT_FROM_EMAIL = "tarhtastyhub@gmail.com"

if "DEVELOPMENT" in os.environ:
    EMAIL_BACKEND = (
        "django.core.mail.backends.console.EmailBackend"
    )
else:
    EMAIL_BACKEND = (
        "django.core.mail.backends.smtp.EmailBackend"
    )
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_HOST_USER = os.environ.get(
        "EMAIL_HOST_USER"
    )
    EMAIL_HOST_PASSWORD = os.environ.get(
        "EMAIL_HOST_PASS"
    )
    DEFAULT_FROM_EMAIL = os.environ.get(
        "DEFAULT_FROM_EMAIL", DEFAULT_FROM_EMAIL
    )

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.template": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
