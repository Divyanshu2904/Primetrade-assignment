from flask import Blueprint, request, jsonify  # pyright: ignore[reportMissingImports]
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  # pyright: ignore[reportMissingImports]
from app import db
from app.models.user import User
from app.utils.helpers import (
    validate_email, validate_password, sanitize_string,
    error_response, success_response
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: johndoe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: User already exists
    """
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    username = sanitize_string(data.get("username", ""), max_length=80)
    email = sanitize_string(data.get("email", ""), max_length=120)
    password = data.get("password", "")

    # Validations
    if not username or len(username) < 3:
        return error_response("Username must be at least 3 characters")
    if not validate_email(email):
        return error_response("Invalid email format")
    is_valid, msg = validate_password(password)
    if not is_valid:
        return error_response(msg)

    # Check duplicates
    if User.query.filter_by(username=username).first():
        return error_response("Username already taken", 409)
    if User.query.filter_by(email=email).first():
        return error_response("Email already registered", 409)

    # Create user
    user = User(username=username, email=email, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return success_response(
        "Registration successful",
        {"user": user.to_dict(), "access_token": token},
        201
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user and get JWT token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful, returns JWT token
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    email = sanitize_string(data.get("email", ""))
    password = data.get("password", "")

    if not email or not password:
        return error_response("Email and password are required")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("Invalid email or password", 401)

    if not user.is_active:
        return error_response("Your account has been deactivated", 403)

    token = create_access_token(identity=user.id)
    return success_response(
        "Login successful",
        {"user": user.to_dict(), "access_token": token}
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get current logged-in user info
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user data
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response("User data retrieved", user.to_dict())
