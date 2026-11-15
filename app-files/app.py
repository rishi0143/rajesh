import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "gobus-secret-key")


@app.before_request
def initialize_database():
    init_db()


@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM buses
        ORDER BY departure_time
    """)

    buses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", buses=buses)


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
            f"Total amount: ₹{total:.2f}",
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


@app.route("/my-bookings")
def my_bookings():

    phone = request.args.get("phone", "")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

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

    cursor.close()
    conn.close()

    return render_template(
        "bookings.html",
        bookings=bookings,
        phone=phone
    )


@app.route("/health")
def health():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.close()
    conn.close()

    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    