import re
from flask import jsonify


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """Min 8 chars, at least 1 letter and 1 number"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Valid"


def sanitize_string(value, max_length=None):
    """Basic string sanitization"""
    if not isinstance(value, str):
        return str(value).strip()
    value = value.strip()
    if max_length:
        value = value[:max_length]
    return value


def error_response(message, status_code=400, errors=None):
    response = {"success": False, "message": message}
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code


def success_response(message, data=None, status_code=200):
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code
