
import os
import hmac
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)

from database import get_connection, init_db

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.before_request
def initialize_database():
    init_db()


# HOME PAGE
@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM buses
            ORDER BY departure_time
        """)
        buses = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("index.html", buses=buses)


# BOOK TICKET
@app.route("/book", methods=["POST"])
def book_ticket():

    passenger = request.form.get("passenger")
    phone = request.form.get("phone")
    bus_id = request.form.get("bus_id")

    try:
        seats = int(request.form.get("seats", 1))
        if seats < 1 or seats > 6:
            raise ValueError
    except ValueError:
        flash("Please select between 1 and 6 seats.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        cursor.execute(
            "SELECT * FROM buses WHERE id=%s FOR UPDATE",
            (bus_id,)
        )
        bus = cursor.fetchone()

        if not bus:
            conn.rollback()
            flash("Bus not found.", "error")
            return redirect(url_for("index"))

        cursor.execute(
            "SELECT COALESCE(SUM(seats), 0) AS booked "
            "FROM bookings WHERE bus_id=%s",
            (bus_id,)
        )
        booked = cursor.fetchone()["booked"]

        if booked + seats > bus["total_seats"]:
            conn.rollback()
            flash("Not enough seats available.", "error")
            return redirect(url_for("index"))

        total = float(bus["price"]) * seats

        cursor.execute("""
            INSERT INTO bookings
            (bus_id, passenger, phone, seats, total_amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (bus_id, passenger, phone, seats, total))

        booking_id = cursor.lastrowid
        conn.commit()

        flash(
            f"Booking successful! Booking ID: {booking_id}. "
            f"Total amount: Rs.{total:.2f}",
            "success"
        )

    except Exception:
        conn.rollback()
        app.logger.exception("Booking failed")
        flash("Booking failed. Please try again.", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("my_bookings", phone=phone))


# MY BOOKINGS
@app.route("/my-bookings")
def my_bookings():

    phone = request.args.get("phone", "")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT bookings.*, buses.operator,
                   buses.source, buses.destination,
                   buses.departure_time
            FROM bookings
            JOIN buses ON bookings.bus_id = buses.id
            WHERE bookings.phone=%s
            ORDER BY bookings.id DESC
        """, (phone,))

        bookings = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "bookings.html",
        bookings=bookings,
        phone=phone
    )


# HEALTH CHECK
@app.route("/health")
def health():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1")
        cursor.fetchone()

        return {
            "status": "healthy",
            "database": "connected"
        }

    finally:
        cursor.close()
        conn.close()


# ADMIN AUTHENTICATION
def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return func(*args, **kwargs)

    return wrapper


# ADMIN LOGIN
@app.route("/owner/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        admin_username = os.getenv("ADMIN_USERNAME", "")
        admin_password = os.getenv("ADMIN_PASSWORD", "")

        if (
            admin_username
            and admin_password
            and hmac.compare_digest(username, admin_username)
            and hmac.compare_digest(password, admin_password)
        ):

            session.clear()
            session["admin_logged_in"] = True

            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password", "error")

    return render_template("admin_login.html")


# ADMIN DASHBOARD
@app.route("/owner/dashboard")
@admin_required
def admin_dashboard():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COUNT(*) AS total_buses
            FROM buses
        """)
        total_buses = cursor.fetchone()["total_buses"]

        cursor.execute("""
            SELECT
                COUNT(*) AS total_bookings,
                COALESCE(SUM(total_amount), 0) AS revenue
            FROM bookings
        """)
        stats = cursor.fetchone()

        cursor.execute("""
            SELECT
                bookings.*,
                buses.operator,
                buses.source,
                buses.destination,
                buses.departure_time
            FROM bookings
            JOIN buses ON bookings.bus_id = buses.id
            ORDER BY bookings.id DESC
        """)
        bookings = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin_dashboard.html",
        total_buses=total_buses,
        total_bookings=stats["total_bookings"],
        revenue=stats["revenue"],
        bookings=bookings
    )


# ADMIN LOGOUT
@app.route("/owner/logout")
@admin_required
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

