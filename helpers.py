import sqlite3
import smtplib

from functools import wraps
from email.message import EmailMessage
from flask import session, redirect, current_app


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def get_db():
    conn = sqlite3.connect(current_app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

# ------------------------------------------------------------
# Email Verification fuction
# ------------------------------------------------------------
# Sends an email verification link using SMTP(Gmail).
# If email credentials are not configured, the verification
# link is printed to the terminal for development/testing.
#
# This fallback behavior ensures the app works in environments
#
# Logic structure assisted by ChatGPT and adapted
# by the author of this project.
# ------------------------------------------------------------
def send_verification_email(to_email, verify_url):
    email_address = current_app.config.get("EMAIL_ADDRESS")
    email_password = current_app.config.get("EMAIL_PASSWORD")

    # If email in not configured
    if not email_address or not email_password:
        print("⚠ Email not configured. Verification link:")
        print(verify_url)
        return


    msg = EmailMessage()
    msg["Subject"] = "Veryfy your FindMyBud account"
    msg["From"] = current_app.config["EMAIL_ADDRESS"]
    msg["To"] = to_email

    msg.set_content(f"""
    HI,

    Thanks for registering on FindMyBud!

    Please verify your email by clicking the link below:
    {verify_url}

    This link will expire in 1 hour.

    If you didn't create this account, you can safely ignore this email.

    -- FindMyBud Team
    """)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(current_app.config["EMAIL_ADDRESS"],
                     current_app.config["EMAIL_PASSWORD"])
        server.send_message(msg)
