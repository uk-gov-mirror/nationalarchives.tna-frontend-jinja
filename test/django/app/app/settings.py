from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "test-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "app.urls"

INSTALLED_APPS = [
    "app",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.forms",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

MIDDLEWARE = []

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "app.jinja2.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

STATIC_URL = "/static/"
USE_TZ = True