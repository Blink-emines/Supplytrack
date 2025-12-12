from django.shortcuts import redirect
from django.urls import reverse

class SecurityCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require authentication
        self.exempt_paths = [
            reverse('security_check'),
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Check if user is authenticated via session
        if not request.session.get('authenticated', False):
            # Check if current path needs protection
            if not any(request.path.startswith(path) for path in self.exempt_paths):
                return redirect(f"{reverse('security_check')}?next={request.path}")
        
        response = self.get_response(request)
        return response