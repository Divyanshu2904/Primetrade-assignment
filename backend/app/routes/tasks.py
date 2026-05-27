from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.task import Task
from app.models.user import User
from app.utils.helpers import sanitize_string, error_response, success_response
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

VALID_STATUSES = ["pending", "in_progress", "completed"]
VALID_PRIORITIES = ["low", "medium", "high"]


@tasks_bp.route("", methods=["GET"])
@jwt_required()
def get_tasks():
    """
    Get all tasks for the logged-in user
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [pending, in_progress, completed]
      - in: query
        name: priority
        type: string
        enum: [low, medium, high]
    responses:
      200:
        description: List of tasks
    """
    user_id = get_jwt_identity()
    query = Task.query.filter_by(user_id=user_id)

    status = request.args.get("status")
    priority = request.args.get("priority")

    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)
    if priority and priority in VALID_PRIORITIES:
        query = query.filter_by(priority=priority)

    tasks = query.order_by(Task.created_at.desc()).all()
    return success_response("Tasks retrieved", [t.to_dict() for t in tasks])


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    """
    Get a single task by ID
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Task data
      404:
        description: Task not found
    """
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return error_response("Task not found", 404)
    return success_response("Task retrieved", task.to_dict())


@tasks_bp.route("", methods=["POST"])
@jwt_required()
def create_task():
    """
    Create a new task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: Buy groceries
            description:
              type: string
              example: Milk, eggs, bread
            status:
              type: string
              enum: [pending, in_progress, completed]
            priority:
              type: string
              enum: [low, medium, high]
            due_date:
              type: string
              example: "2024-12-31T23:59:59"
    responses:
      201:
        description: Task created
      400:
        description: Validation error
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    title = sanitize_string(data.get("title", ""), max_length=200)
    if not title:
        return error_response("Title is required")

    description = sanitize_string(data.get("description", ""), max_length=2000) or None
    status = data.get("status", "pending")
    priority = data.get("priority", "medium")

    if status not in VALID_STATUSES:
        return error_response(f"Status must be one of: {', '.join(VALID_STATUSES)}")
    if priority not in VALID_PRIORITIES:
        return error_response(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")

    due_date = None
    if data.get("due_date"):
        try:
            due_date = datetime.fromisoformat(data["due_date"])
        except ValueError:
            return error_response("Invalid due_date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)")

    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        user_id=user_id
    )
    db.session.add(task)
    db.session.commit()
    return success_response("Task created successfully", task.to_dict(), 201)


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    """
    Update a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            status:
              type: string
              enum: [pending, in_progress, completed]
            priority:
              type: string
              enum: [low, medium, high]
            due_date:
              type: string
    responses:
      200:
        description: Task updated
      404:
        description: Task not found
    """
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return error_response("Task not found", 404)

    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    if "title" in data:
        title = sanitize_string(data["title"], max_length=200)
        if not title:
            return error_response("Title cannot be empty")
        task.title = title

    if "description" in data:
        task.description = sanitize_string(data["description"], max_length=2000) or None

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return error_response(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        task.status = data["status"]

    if "priority" in data:
        if data["priority"] not in VALID_PRIORITIES:
            return error_response(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")
        task.priority = data["priority"]

    if "due_date" in data:
        if data["due_date"]:
            try:
                task.due_date = datetime.fromisoformat(data["due_date"])
            except ValueError:
                return error_response("Invalid due_date format. Use ISO 8601")
        else:
            task.due_date = None

    task.updated_at = datetime.utcnow()
    db.session.commit()
    return success_response("Task updated successfully", task.to_dict())


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    """
    Delete a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Task deleted
      404:
        description: Task not found
    """
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return error_response("Task not found", 404)

    db.session.delete(task)
    db.session.commit()
    return success_response("Task deleted successfully")
