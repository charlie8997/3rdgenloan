from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import logging
import traceback
import time

logger = logging.getLogger(__name__)


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Resolve common public prefixes from settings with sane defaults.
        static_url = getattr(settings, 'STATIC_URL', '/static/') or '/static/'
        media_url = getattr(settings, 'MEDIA_URL', '/media/') or '/media/'
        admin_url = getattr(settings, 'ADMIN_URL', '/admin/') or '/admin/'

        # Fast-path: do not process admin or static/media asset requests.
        if path.startswith(static_url) or path.startswith(media_url) or path.startswith(admin_url):
            # Write a short record for admin requests so we can inspect incoming
            # requests on the instance when external logs are missing.
            if path.startswith(admin_url):
                try:
                    with open('/tmp/admin_requests.log', 'a') as f:
                        f.write(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                        f.write(f"METHOD={request.method} PATH={path} QUERY={request.META.get('QUERY_STRING','')}\n")
                        f.write(f"REMOTE_ADDR={request.META.get('REMOTE_ADDR','unknown')} USER_AGENT={request.META.get('HTTP_USER_AGENT','-')}\n")
                        f.write(f"AUTHENTICATED={getattr(request.user, 'is_authenticated', False)} PRINCIPAL={getattr(getattr(request.user, 'username', None), '__str__', lambda: '')()}\n")
                except Exception:
                    pass
            return self.get_response(request)

        try:
            if request.user.is_authenticated:
                # Only for non-admin users
                if hasattr(request.user, 'profile') and not request.user.profile.completed:
                    if request.path not in [reverse('profile_complete'), reverse('logout')]:
                        return redirect('profile_complete')
                # Enforce bank details after profile completion
                if (
                    hasattr(request.user, 'profile') and request.user.profile.completed
                    and not hasattr(request.user, 'bank_detail')
                ):
                    if request.path not in [reverse('bank_detail'), reverse('logout')]:
                        return redirect('bank_detail')
        except Exception:
            # Defensive: log and continue so middleware errors don't 500 the admin or static
            logger.exception('ProfileCompletionMiddleware error')
            # Also write a minimal traceback to a tmp file so it can be inspected
            # from the running instance when `fly logs` doesn't include the trace.
            try:
                if path.startswith(admin_url):
                    with open('/tmp/admin_exceptions.log', 'a') as f:
                        f.write(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} PATH={path} ---\n")
                        traceback.print_exc(file=f)
            except Exception:
                # best-effort file logging; swallow any errors
                pass

        return self.get_response(request)
