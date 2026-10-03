import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/local_services")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer")

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(40), default="bi-tools")

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    booking_date = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(30), default="Pending")
    customer = db.relationship("User", backref="bookings")
    service = db.relationship("Service")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def seed_services():
    if Service.query.count() == 0:
        data = [
            ("Home Cleaning", "Cleaning", "Deep cleaning and regular home cleaning services.", 799, "bi-house"),
            ("Electrician", "Repairs", "Electrical repairs, fittings, and troubleshooting.", 499, "bi-lightning-charge"),
            ("Plumbing", "Repairs", "Tap repairs, leak fixes, and bathroom plumbing.", 399, "bi-droplet"),
            ("AC Repair", "Appliance", "AC servicing, installation, and repair.", 699, "bi-snow"),
            ("Painting", "Home Improvement", "Interior touch-ups and complete room painting.", 1499, "bi-brush"),
            ("Carpentry", "Home Improvement", "Furniture repair, shelves, and woodwork.", 599, "bi-hammer"),
        ]
        for title, category, description, price, icon in data:
            db.session.add(Service(title=title, category=category, description=description, price=price, icon=icon))
        db.session.commit()

@app.route("/")
def index():
    services = Service.query.order_by(Service.id).limit(6).all()
    return render_template("index.html", services=services)

@app.route("/services")
def services():
    q = request.args.get("q", "").strip()
    query = Service.query
    if q:
        query = query.filter(db.or_(Service.title.ilike(f"%{q}%"), Service.category.ilike(f"%{q}%")))
    return render_template("services.html", services=query.order_by(Service.title).all(), q=q)

@app.route("/book/<int:service_id>", methods=["GET", "POST"])
@login_required
def book(service_id):
    service = db.session.get(Service, service_id)
    if not service:
        flash("Service not found.", "danger")
        return redirect(url_for("services"))
    if request.method == "POST":
        date = request.form.get("booking_date", "")
        address = request.form.get("address", "").strip()
        notes = request.form.get("notes", "").strip()
        if not date or not address:
            flash("Please provide a date and address.", "warning")
        else:
            booking = Booking(customer_id=current_user.id, service_id=service.id, booking_date=date, address=address, notes=notes)
            db.session.add(booking)
            db.session.commit()
            flash("Your booking request has been submitted!", "success")
            return redirect(url_for("dashboard"))
    return render_template("booking.html", service=service, today=date.today().isoformat())

@app.route("/dashboard")
@login_required
def dashboard():
    bookings = Booking.query.filter_by(customer_id=current_user.id).order_by(Booking.id.desc()).all()
    return render_template("dashboard.html", bookings=bookings)

@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("admin.html", bookings=Booking.query.order_by(Booking.id.desc()).all(),
                           services=Service.query.count(), users=User.query.count())

@app.route("/admin/booking/<int:booking_id>/<status>", methods=["POST"])
@login_required
def update_booking(booking_id, status):
    if current_user.role != "admin" or status not in ("Confirmed", "Completed", "Cancelled"):
        flash("You are not allowed to perform that action.", "danger")
        return redirect(url_for("index"))
    booking = db.session.get(Booking, booking_id)
    if booking:
        booking.status = status
        db.session.commit()
        flash("Booking status updated.", "success")
    return redirect(url_for("admin"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter your name, a valid email, and a password of at least 6 characters.", "warning")
        elif User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
        else:
            user = User(name=name, email=email, password=generate_password_hash(password), role="customer")
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Welcome! Your account is ready.", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("admin" if user.role == "admin" else "dashboard"))
        flash("Incorrect email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.cli.command("init-db")
def init_db():
    """Create tables and starter service listings."""
    db.create_all()
    seed_services()
    print("Database initialized.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_services()
    app.run(debug=True)
