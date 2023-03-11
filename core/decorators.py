from functools import wraps
from django.shortcuts import redirect

# admin login required 
def admin_login_required(func, REDIRECT_URL = 'home'):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/accounts/login")
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        return redirect(REDIRECT_URL)
    return wrap

