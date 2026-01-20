import os
from .base import *

# Production overrides — keep these explicit and environment-driven.
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Secret key (must be set in environment/secrets).
SECRET_KEY = os.getenv('SECRET_KEY', 'changeme-insecure')

# Optional production domain used elsewhere in the project.
PROD_DOMAIN = os.getenv('PROD_DOMAIN', '3rdgenloan.online')

# ALLOWED_HOSTS: either provide a comma-separated env var or fall back to sensible defaults.
env_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '')
if env_hosts:
	ALLOWED_HOSTS = [h.strip() for h in env_hosts.split(',') if h.strip()]
else:
	ALLOWED_HOSTS = ['3rdgenloan.online', 'www.3rdgenloan.online']

# CSRF trusted origins must include scheme; derive from ALLOWED_HOSTS for convenience.
CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
	if host.startswith('http://') or host.startswith('https://'):
		CSRF_TRUSTED_ORIGINS.append(host)
	else:
		CSRF_TRUSTED_ORIGINS.append(f"https://{host}")

# Standard proxy header when behind a proxy/load-balancer
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Email backend (use Fly secrets to set these in production)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 1025))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# Use WhiteNoise's compressed storage (non-manifest) to avoid runtime manifest lookup errors.
# This is intentionally conservative: switch to the manifest-backed storage once build
# processes reliably produce staticfiles.json.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# --- Security settings ---
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
