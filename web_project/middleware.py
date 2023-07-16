from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.session.get_expiry_age() <= 0:
            # Session has expired
            messages.warning(request, 'Your session has expired. Please login again.')
            return redirect(reverse('authentication:login')) # Redirect to login page

        response = self.get_response(request)
        return response
