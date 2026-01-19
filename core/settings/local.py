from .base import *

# Local/development overrides
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Allow local dev origins for CSRF
CSRF_TRUSTED_ORIGINS = [
	"http://127.0.0.1:8000",
	"http://localhost:8000",
    "http://192.168.1.76:8000",
]

# Optionally, load local .env here if needed

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
