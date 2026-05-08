from app import create_app, db
from app.models.user import User
from app.models.task import Task


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Task": Task}


@app.cli.command("create-admin")
def create_admin():
    """Create a default admin user"""
    from app import bcrypt
    existing = User.query.filter_by(email="admin@Primetrade-assignment.com").first()
    if existing:
        print("Admin already exists!")
        return

    admin = User(
        username="admin",
        email="admin@Primetrade-assignment.com",
        role="admin"
    )
    admin.set_password("Admin@123")
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin user created!")
    print("   Email: admin@Primetrade-assignment.com")
    print("   Password: Admin@123")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
