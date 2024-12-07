import random
from flask import Flask, render_template, request, redirect, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

def send_email(email, otp):
    """Send OTP via email."""
    msg = Message("Your OTP Code", sender="majoka193@gmail.com", recipients=[email])
    msg.body = f"Your OTP is: {otp}"
    mail.send(msg)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        otp = request.form.get("otp")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not registered. Please sign up first.", "error")
            return render_template("login.html", otp_sent=False, email=email)

        if not session.get("otp_stage"):
            if user.password != password:
                flash("Incorrect password. Please try again.", "error")
                return render_template("login.html", otp_sent=False, email=email)

            otp = random.randint(100000, 999999)
            session["email"] = email
            session["authenticated"] = False
            session["login_otp"] = otp
            session["otp_sent_time"] = datetime.now(timezone.utc)
            session["otp_stage"] = True
            send_email(email, otp)
            flash("OTP sent to your email. Please verify.", "info")
            return render_template("login.html", otp_sent=True, email=email, password=password)

        if session.get("otp_stage"):
            otp_sent_time = session.get("otp_sent_time")
            if otp_sent_time and datetime.now(timezone.utc) - otp_sent_time > timedelta(minutes=2):
                flash("OTP expired. Please try again.", "error")
                session.pop("otp_stage", None)
                return render_template("login.html", otp_sent=False, email=email)

            if str(session.get("login_otp")) == otp:
                session["authenticated"] = True
                session.pop("otp_stage", None)
                return redirect("/home")
            else:
                flash("Invalid OTP. Please try again.", "error")
                return render_template("login.html", otp_sent=True, email=email, password=password)

    return render_template("login.html", otp_sent=False)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect("/signup")
    
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered! Please login.", "info")
            return redirect("/")

        otp = random.randint(100000, 999999)
        session["signup_email"] = email
        session["signup_password"] = password
        session["signup_confirm_password"] = confirm_password
        session["signup_otp"] = otp
        session["otp_sent_time"] = datetime.now(timezone.utc)

        send_email(email, otp)

        return render_template("signup.html", otp_sent=True, email=email, password=password, confirm_password=confirm_password)

    return render_template("signup.html", otp_sent=False)

@app.route("/verify_signup", methods=["GET", "POST"])
def verify_signup():
    entered_otp = request.form.get("otp")

    otp_sent_time = session.get("otp_sent_time")
    if otp_sent_time and datetime.now(timezone.utc) - otp_sent_time > timedelta(minutes=5):
        flash("OTP expired. Please try again.")
        return redirect("/signup")
    
    if str(session.get("signup_otp")) == entered_otp:
        new_user = User(email=session["signup_email"], password=session["signup_password"])
        db.session.add(new_user)
        db.session.commit()

        session.clear()
        session["email"] = new_user.email
        session["authenticated"] = True

        flash("Account created successfully. Welcome to the home page!")
        return redirect("/home")
    else:
        flash("Invalid OTP!", "error")
        return redirect("/signup")

@app.route("/home")
def home():
    if not session.get("authenticated"):
        return redirect("/")
    return render_template("home.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)