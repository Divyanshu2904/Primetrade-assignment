from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.models.task import Task
from app.middleware.auth import admin_required
from app.utils.helpers import error_response, success_response
from app import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    """
    Get all users (Admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: List of all users
      403:
        description: Admin access required
    """
    users = User.query.all()
    return success_response("All users retrieved", [u.to_dict() for u in users])


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["PATCH"])
@admin_required
def deactivate_user(user_id):
    """
    Deactivate a user account (Admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: User deactivated
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    user.is_active = False
    db.session.commit()
    return success_response("User deactivated", user.to_dict())


@admin_bp.route("/users/<int:user_id>/activate", methods=["PATCH"])
@admin_required
def activate_user(user_id):
    """
    Activate a user account (Admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: User activated
    """
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    user.is_active = True
    db.session.commit()
    return success_response("User activated", user.to_dict())


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """
    Get platform statistics (Admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Platform stats
    """
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_tasks = Task.query.count()
    pending_tasks = Task.query.filter_by(status="pending").count()
    completed_tasks = Task.query.filter_by(status="completed").count()

    return success_response("Stats retrieved", {
        "users": {"total": total_users, "active": active_users},
        "tasks": {
            "total": total_tasks,
            "pending": pending_tasks,
            "completed": completed_tasks,
            "in_progress": total_tasks - pending_tasks - completed_tasks
        }
    })


@admin_bp.route("/tasks", methods=["GET"])
@admin_required
def get_all_tasks():
    """
    Get all tasks across all users (Admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: All tasks
    """
    tasks = Task.query.all()
    return success_response("All tasks retrieved", [t.to_dict() for t in tasks])
