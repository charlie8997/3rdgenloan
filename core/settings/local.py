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

# Email backend (inherits from .env defaults)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 1025))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '3rd Gen Loan Inc <support@3rdgenloan.online>')
