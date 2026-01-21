import os
import secrets
import sqlite3

from flask import Flask, render_template, request, redirect, flash, session, url_for, abort
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer

from helpers import login_required, get_db, send_verification_email


# Configure application
app = Flask(__name__)

# Database path
app.config["DATABASE"] = os.path.join(app.instance_path, "findmybud.db")
os.makedirs(app.instance_path, exist_ok=True)

# Upload folder for future
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ------------------------------------------------------------
# Email Configuration
# ------------------------------------------------------------
# This project uses environment variables for email credentials
# (EMAIL_ADDRESS and EMAIL_PASSWORD) to avoid hardcoding secrets.
#
# If these variables are not set, the application will still run
# safely without crashing.
#
# Design and security approach assisted by ChatGPT,
# reviewed and implemented by the project author.
# ------------------------------------------------------------
# SMTP configuration
app.secret_key = secrets.token_hex(32)
app.config["EMAIL_ADDRESS"] = os.environ.get("EMAIL_ADDRESS")
app.config["EMAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD")

# Configure serializer
serializer = URLSafeTimedSerializer(app.secret_key)


# Basic routes
@app.route("/")
def index():
    db = get_db()

    reports = db.execute("""  SELECT reports.*, users.name as user_name
    FROM reports
    JOIN users ON reports.user_id = users.id
    ORDER BY reports.created_at DESC
    """).fetchall()

    return render_template("index.html", reports=reports)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate that all required fileds are filledn
        if not name or not email or not password or not confirmation:
            flash("Not Registered! Please fill all the required fields.")
            return redirect("/register")

        # Check the password and confirmation match
        if password != confirmation:
            flash("Not Registered!Error: Passwords must match.")
            return redirect("/register")

        # Converting password into hash form
        password_hash = generate_password_hash(password)

        # Insert user into database
        db = get_db()

        try:
            db.execute("INSERT INTO users (name, phone, email, password_hash) VALUES (?, ?, ?, ?)",
            (name, phone, email, password_hash))
            db.commit()
        except sqlite3.IntegrityError:
            flash("Error: Email already exists!")
            return redirect("/register")
        # Get auto user id
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        token = serializer.dumps(email, salt="email-verify")

        verify_url = url_for(
            "verify_email", token=token, _external=True
        )

        ### send_verification_email(email, verify_url)

        flash("Registration successful! Please check your email to verify your account.")
        return redirect("/login")

    return render_template("register.html", title="register", button_text="register", action="/register")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # Forget any user
        session.clear()

        # Get form data
        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure email and password was submitted
        if not request.form.get("email") or not request.form.get("password"):
            flash("Please provide email and password!")
            return redirect("/login")

        # Query database for email
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?",
                          (request.form.get("email"),)).fetchone()

        # Ensure email exists and password is correct
        if user is None:
            flash("Invalid email or password")
            return redirect("/login")

        # Validate user verification
        if user["is_verified"] == 0:
            flash("Please verify your email before logging in.")
            return redirect("/login")

        # Check password
        if not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = user["id"]

        flash("Welcome!")
        return redirect("/")

    return render_template("login.html", title="Login", action=f"/login", button_text="Login")


@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    mode = request.args.get("mode", "lost")

    # Mode validation
    if mode not in ("lost", "found"):
        flash("Invalid report type.")
        return redirect("/")

    # Get form data
    if request.method == "POST":
        brand = request.form.get("brand")
        model = request.form.get("model")
        part = request.form.get("part")
        color = request.form.get("color")
        date = request.form.get("date")
        location_text = request.form.get("location_text")
        description = request.form.get("description")

        # Images
        photo1 = request.files.get("photo1")
        photo2 = request.files.get("photo2")

        # Save photo if uploaded
        saved_photo1 = None
        saved_photo2 = None

        upload_dir = app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)

        if photo1 and photo1.filename:
            filename1 = secure_filename(photo1.filename)
            saved_photo1 = filename1
            photo1.save(os.path.join(upload_dir, filename1))

        if photo2 and photo2.filename:
            filename2 = secure_filename(photo2.filename)
            saved_photo2 = filename2
            photo2.save(os.path.join(upload_dir, filename2))

        # Insert into database
        db = get_db()
        db.execute(""" INSERT INTO reports (user_id, type, brand, model, part, color, event_date, location_text, description, photo1, photo2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, (
            session["user_id"],
            mode,
            brand,
            model,
            part,
            color,
            date,
            location_text,
            description,
            saved_photo1,
            saved_photo2
        ))
        db.commit()

        flash("Report submitted successfully!")
        return redirect("/")

    return render_template("report.html", title=f"Report {mode.capitalize()} Earbud", action="/report?mode=" + mode, button_text="Submit Report",  mode=mode)


@app.route("/logout")
def logout():
    session.clear()

    flash("You have been logged out.")
    return redirect("/login")


@app.route("/report/<int:report_id>")
@login_required
def report_details(report_id):
    db = get_db()

    report = db.execute("""
        SELECT reports.*, users.name AS user_name, users.email as user_email
        FROM reports
        JOIN users ON reports.user_id = users.id
        WHERE reports.id = ?
        """,
                        (report_id,)
                        ).fetchone()

    if report is None:
        flash("Report not found")
        return redirect("/")

    return render_template("report_details.html", report=report)


@app.route("/verify/<token>")
def verify_email(token):
    try:
        email = serializer.loads(
            token, salt="email-verify", max_age=3600
        )
    except:
        flash("verification link is invalid or expired.")
        return redirect("/login")

    db = get_db()
    db.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
    db.commit()

    flash("Email verified successfully! You can now log in.")
    return redirect("/login")


@app.route("/my-reports")
@login_required
def my_reports():
    db = get_db()

    reports = db.execute("""
        SELECT reports.*, users.name as user_name
        FROM reports
        JOIN users ON reports.user_id = users.id
        WHERE reports.user_id = ?
        ORDER BY reports.created_at DESC
    """, (session["user_id"],)).fetchall()

    return render_template("my_reports.html", reports=reports)


@app.route("/report/<int:report_id>/resolve", methods=["POST"])
@login_required
def resolve_report(report_id):
    db = get_db()

    # ensure the report belongs to the logged-in user
    report = db.execute(
        "SELECT * FROM reports WHERE id = ? AND user_id = ?",
        (report_id, session["user_id"])
    ).fetchone()

    if report is None:
        flash("Unauthorized action.")
        return redirect("/my-reports")

    db.execute(
        "UPDATE reports SET status = 'resolved' WHERE id = ?",
        (report_id,)
    )
    db.commit()

    flash("Report marked as resolved.")
    return redirect("/my-reports")


@app.route("/report/<int:report_id>/delete", methods=["POST"])
@login_required
def delete_report(report_id):
    db = get_db()

    # Ensure the report belongs to the logged-in user
    report = db.execute(
        "SELECT * FROM reports WHERE id = ? AND user_id = ?",
        (report_id, session["user_id"])
    ).fetchone()

    if report is None:
        abort(403)

    # Check

    db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    db.commit()

    flash("Report deleted successfully.")
    return redirect("/my-reports")
