from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
        return self.get_response(request)
