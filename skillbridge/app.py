"""
SkillBridge - beginner-friendly Flask web application.

Run locally:
    python -m venv venv
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    pip install -r requirements.txt
    python app.py

The app uses SQLite by default so it is easy to run.
To use Supabase PostgreSQL, set DATABASE_URL in your environment.
"""
import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")

# SQLite is the easiest database for first-time local setup.
# Later, set DATABASE_URL to your Supabase PostgreSQL connection string.
database_url = os.environ.get("DATABASE_URL", "sqlite:///skillbridge.db")

# Some hosting providers give PostgreSQL URLs beginning with postgres://.
# SQLAlchemy expects postgresql://, so convert the prefix when needed.
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------------
# Database tables
# ----------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100), default="")
    year = db.Column(db.String(30), default="")
    skills = db.Column(db.String(500), default="")  # Stored as comma-separated words.


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_needed = db.Column(db.String(300), nullable=False)
    level = db.Column(db.String(30), default="Beginner")
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    owner = db.relationship("User", backref="created_projects")


class PartnerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])


class ProjectRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    project = db.relationship("Project", backref="join_requests")
    sender = db.relationship("User", foreign_keys=[sender_id])


def seed_demo_students():
    """Add fictional student profiles so Team Finder has sample data."""
    demo_students = [
        {"name": "Aarav Sharma", "email": "aarav.demo@example.com", "department": "Computer Science", "year": "2nd Year", "skills": "Python,HTML,CSS,Flask"},
        {"name": "Diya Nair", "email": "diya.demo@example.com", "department": "Computer Science", "year": "3rd Year", "skills": "Java,SQL,JavaScript"},
        {"name": "Rohan Kumar", "email": "rohan.demo@example.com", "department": "Information Science", "year": "2nd Year", "skills": "C++,Python,Data Structures"},
        {"name": "Meera Rao", "email": "meera.demo@example.com", "department": "Computer Science", "year": "3rd Year", "skills": "UI Design,HTML,CSS,Figma"},
        {"name": "Ishaan Patel", "email": "ishaan.demo@example.com", "department": "Electronics", "year": "2nd Year", "skills": "Python,Arduino,IoT"},
        {"name": "Ananya Das", "email": "ananya.demo@example.com", "department": "Computer Science", "year": "4th Year", "skills": "JavaScript,React,Node.js"},
        {"name": "Kabir Singh", "email": "kabir.demo@example.com", "department": "Information Science", "year": "3rd Year", "skills": "Python,SQL,Machine Learning"},
        {"name": "Sana Khan", "email": "sana.demo@example.com", "department": "Computer Science", "year": "2nd Year", "skills": "Java,HTML,CSS,MySQL"},
    ]

    for student in demo_students:
        # Check by email so restarting the app never creates duplicate students.
        if not User.query.filter_by(email=student["email"]).first():
            new_student = User(
                name=student["name"],
                email=student["email"],
                password_hash=generate_password_hash("Student@123"),
                department=student["department"],
                year=student["year"],
                skills=student["skills"]
            )
            db.session.add(new_student)

    db.session.commit()

def login_required(view_function):
    """Send visitors to the login page if they are not signed in."""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to view your dashboard.", "info")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)
    return wrapped_view


def get_current_user():
    """Return the signed-in user's database record."""
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


def seed_projects():
    """Add sample projects the first time the app starts."""
    if Project.query.count() == 0:
        sample_projects = [
            Project(
                title="Student Notes Sharing Portal",
                description="Build a website where students can upload, organize and find subject notes.",
                skills_needed="HTML,CSS,JavaScript,Python,Flask,SQL",
                level="Beginner"
            ),
            Project(
                title="Campus Event Manager",
                description="Create a platform to publish college events and allow students to register.",
                skills_needed="HTML,CSS,JavaScript,Python,Flask",
                level="Intermediate"
            ),
            Project(
                title="Personal Expense Tracker",
                description="Create a simple application to record expenses and view monthly summaries.",
                skills_needed="Python,Flask,SQL,JavaScript",
                level="Beginner"
            ),
            Project(
                title="Portfolio Website",
                description="Create a personal portfolio to showcase skills, certificates and projects.",
                skills_needed="HTML,CSS,JavaScript",
                level="Beginner"
            ),
            Project(
                title="Library Management System",
                description="Manage books, members, borrowing and return records.",
                skills_needed="Python,SQL,Flask",
                level="Intermediate"
            ),
        ]
        demo_owner = User.query.filter_by(email="aarav.demo@example.com").first()
        for sample_project in sample_projects:
            sample_project.owner_id = demo_owner.id if demo_owner else None
        db.session.add_all(sample_projects)
        db.session.commit()


@app.route("/")
def home():
    return render_template("index.html", user=get_current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Use a password with at least 6 characters.", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        flash("Your account has been created. Welcome to SkillBridge!", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            flash("You are now logged in.", "success")
            return redirect(url_for("dashboard"))

        flash("Incorrect email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    return render_template("dashboard.html", user=user)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()

    if request.method == "POST":
        user.department = request.form.get("department", "").strip()
        user.year = request.form.get("year", "").strip()
        user.skills = request.form.get("skills", "").strip()
        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


@app.route("/projects")
@login_required
def projects():
    user = get_current_user()
    all_projects = Project.query.order_by(Project.title).all()

    # Simple matching: count how many required skills the student has.
    student_skills = {
        skill.strip().lower()
        for skill in user.skills.split(",")
        if skill.strip()
    }

    project_results = []
    for project in all_projects:
        required_skills = [
            skill.strip()
            for skill in project.skills_needed.split(",")
            if skill.strip()
        ]

        matched_skills = [
            skill for skill in required_skills
            if skill.lower() in student_skills
        ]

        if required_skills:
            match_percentage = round(
                len(matched_skills) / len(required_skills) * 100
            )
        else:
            match_percentage = 0

        project_results.append({
            "project": project,
            "matched_skills": matched_skills,
            "match_percentage": match_percentage
        })

    # Show the projects with the highest matching percentage first.
    project_results.sort(
        key=lambda result: result["match_percentage"],
        reverse=True
    )

    return render_template(
        "projects.html",
        user=user,
        project_results=project_results
    )


@app.route("/team-finder")
@login_required
def team_finder():
    user = get_current_user()
    # Do not show the currently signed-in student in their own search results.
    students = User.query.filter(User.id != user.id).order_by(User.name).all()
    return render_template("team_finder.html", user=user, students=students)


@app.route("/partner-request/<int:student_id>", methods=["POST"])
@login_required
def partner_request(student_id):
    user = get_current_user()
    target = db.session.get(User, student_id)
    if not target or target.id == user.id:
        flash("That student is not available.", "error")
    elif PartnerRequest.query.filter_by(sender_id=user.id, receiver_id=target.id, status="Pending").first():
        flash("You already have a pending request to this student.", "info")
    elif PartnerRequest.query.filter_by(sender_id=target.id, receiver_id=user.id, status="Pending").first():
        flash("This student has already requested to partner with you. Check My Requests.", "info")
    else:
        db.session.add(PartnerRequest(sender_id=user.id, receiver_id=target.id))
        db.session.commit()
        flash("Partnership request sent!", "success")
    return redirect(url_for("team_finder"))


@app.route("/project-request/<int:project_id>", methods=["POST"])
@login_required
def project_request(project_id):
    user = get_current_user()
    project = db.session.get(Project, project_id)
    if not project:
        flash("Project not found.", "error")
    elif project.owner_id == user.id:
        flash("You created this project, so you cannot request to join it.", "info")
    elif ProjectRequest.query.filter_by(project_id=project.id, sender_id=user.id, status="Pending").first():
        flash("You already sent a pending request for this project.", "info")
    else:
        db.session.add(ProjectRequest(project_id=project.id, sender_id=user.id))
        db.session.commit()
        flash("Project join request sent!", "success")
    return redirect(url_for("projects"))


@app.route("/my-requests")
@login_required
def my_requests():
    user = get_current_user()
    incoming_partners = PartnerRequest.query.filter_by(receiver_id=user.id).order_by(PartnerRequest.created_at.desc()).all()
    outgoing_partners = PartnerRequest.query.filter_by(sender_id=user.id).order_by(PartnerRequest.created_at.desc()).all()
    incoming_projects = ProjectRequest.query.join(Project).filter(Project.owner_id == user.id).order_by(ProjectRequest.created_at.desc()).all()
    outgoing_projects = ProjectRequest.query.filter_by(sender_id=user.id).order_by(ProjectRequest.created_at.desc()).all()
    return render_template("my_requests.html", user=user,
        incoming_partners=incoming_partners, outgoing_partners=outgoing_partners,
        incoming_projects=incoming_projects, outgoing_projects=outgoing_projects)


@app.route("/request-action/<string:request_type>/<int:request_id>/<string:action>", methods=["POST"])
@login_required
def request_action(request_type, request_id, action):
    user = get_current_user()
    if action not in ["accept", "reject"]:
        flash("Invalid request action.", "error")
        return redirect(url_for("my_requests"))
    new_status = "Accepted" if action == "accept" else "Rejected"

    if request_type == "partner":
        item = db.session.get(PartnerRequest, request_id)
        allowed = item and item.receiver_id == user.id
    elif request_type == "project":
        item = db.session.get(ProjectRequest, request_id)
        allowed = item and item.project.owner_id == user.id
    else:
        item, allowed = None, False

    if not allowed:
        flash("You cannot update this request.", "error")
    elif item.status != "Pending":
        flash("This request has already been answered.", "info")
    else:
        item.status = new_status
        db.session.commit()
        flash(f"Request {new_status.lower()}.", "success")
    return redirect(url_for("my_requests"))


@app.route("/about")
def about():
    return render_template("about.html", user=get_current_user())


@app.route("/contact")
def contact():
    return render_template("contact.html", user=get_current_user())


# Create database tables and sample project data when the app starts.
with app.app_context():
    db.create_all()

    # Small migration for students updating from the earlier SkillBridge ZIP.
    # It adds the project owner column without deleting their existing accounts.
    from sqlalchemy import inspect
    project_columns = [column["name"] for column in inspect(db.engine).get_columns("project")]
    if "owner_id" not in project_columns:
        db.session.execute(db.text("ALTER TABLE project ADD COLUMN owner_id INTEGER REFERENCES user(id)"))
        db.session.commit()

    seed_demo_students()
    seed_projects()

    # Give the original sample projects a demo owner after an older database is updated.
    demo_owner = User.query.filter_by(email="aarav.demo@example.com").first()
    if demo_owner:
        Project.query.filter(Project.owner_id.is_(None)).update({"owner_id": demo_owner.id}, synchronize_session=False)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
