from django.conf import settings

def site_settings(request):
    """Expose a small set of settings to templates (safe, non-secret)."""
    return {
        'LOGIN_URL': getattr(settings, 'LOGIN_URL', '/login/'),
        'ORG_DISPLAY_NAME': getattr(settings, 'ORG_DISPLAY_NAME', '3rd Gen Loan'),
    }
