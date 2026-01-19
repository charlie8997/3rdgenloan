from .base import *

# Production overrides
import os
DEBUG = False
# Build allowed hosts list from Fly app name plus optional env overrides
fly_app = os.getenv('FLY_APP_NAME')
allowed_hosts = []
trusted_origins = []
if fly_app:
	fly_host = f"{fly_app}.fly.dev"
	allowed_hosts.append(fly_host)
	trusted_origins.append(f"https://{fly_host}")
default_domains = ['3rdgenloan.online', 'www.3rdgenloan.online']
allowed_hosts.extend(default_domains)
trusted_origins.extend([f"https://{domain}" for domain in default_domains])
custom_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '')
if custom_hosts:
	for host in [h.strip() for h in custom_hosts.split(',') if h.strip()]:
		allowed_hosts.append(host)
		if host.startswith('http://') or host.startswith('https://'):
			trusted_origins.append(host)
		else:
			trusted_origins.append(f"https://{host}")
ALLOWED_HOSTS = allowed_hosts or ['.fly.dev']
# Align CSRF trusted origins with allowed hosts for HTTPS
CSRF_TRUSTED_ORIGINS = trusted_origins
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Use environment variable for secret key
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-insecure")


# Email backend for production (Namecheap custom email)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.3rdgenloan.online'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'admin@3rdgenloan.online'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = '3rd Gen Loan <admin@3rdgenloan.online>'

# --- Recommended Security Settings ---
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
