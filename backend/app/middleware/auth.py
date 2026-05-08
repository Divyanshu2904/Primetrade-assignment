from functools import wraps
import importlib
from flask import jsonify
from app.models.user import User

_jwt = importlib.import_module("flask_jwt_extended")
verify_jwt_in_request = _jwt.verify_jwt_in_request
get_jwt_identity = _jwt.get_jwt_identity


def admin_required(fn):
    """Decorator to allow only admin users"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"success": False, "message": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def active_user_required(fn):
    """Decorator to ensure user is active"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({"success": False, "message": "Account is inactive"}), 403
        return fn(*args, **kwargs)
    return wrapper
