"""Views."""

from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login


def home(request):
    """Home page."""
    if request.user.is_authenticated:
        login(request, request.user)
        return redirect('todo:mine')
    else:
        return redirect(settings.LOGIN_URL)
