import os
import string

from functools import wraps
from django.shortcuts import render, redirect

from tach.settings import HOSTNAME, ADMIN_ROLES


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from tach.frame import UNAUTHORIZED_USER
        request = args[0]
        if not getattr(request, 'account', False):
            login_page = "/login/login_form?disable_cookie_login__=1&came_from=%s" % HOSTNAME
            return redirect(login_page)
        if request.account is UNAUTHORIZED_USER:
            return render(request, 'restricted.html')
        return func(*args, **kwargs)
    return wrapper


def auth_details_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.account.country:
            return redirect('overview')
        return func(*args, **kwargs)
    return wrapper


def auth_admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if getattr(request, 'account', False):
            if getattr(request.account, 'roles', False):
                for r in request.account.roles:
                    if r in ADMIN_ROLES:
                        return func(*args, **kwargs)
        return render(request, 'restricted.html')
    return wrapper


def random_string(length, stringset=string.ascii_letters+string.digits):
    '''
    Returns a string with `length` characters chosen from `stringset`
    >>> len(generate_random_string(20) == 20
    '''
    return ''.join([stringset[i%len(stringset)] \
        for i in [ord(x) for x in os.urandom(length)]])