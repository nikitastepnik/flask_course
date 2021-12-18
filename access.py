from flask import session, current_app, request, render_template
from functools import wraps


def is_group_valid():
    group_name = session.get('group_name', '')
    if group_name:
        return True
    else:
        return False


def group_validation_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if is_group_valid():
            return f(*args, **kwargs)
        return 'Permission denied'

    return wrapper


def group_permission_valid():
    config = current_app.config['ACCESS_CONFIG']
    group_name = session.get('group_name', 'unauthorized')
    target_app = "" if len(request.endpoint.split('.')) == 1 else request.endpoint.split('.')[0]
    if group_name in config and target_app in config[group_name]:
        return True
    return False


def group_permission_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if group_permission_valid():
            return f(*args, **kwargs)
        return render_template('error.html')

    return wrapper
