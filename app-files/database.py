import os
import mysql.connector


def get_connection():

    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        connection_timeout=10
    )


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            operator VARCHAR(100) NOT NULL,
            source VARCHAR(100) NOT NULL,
            destination VARCHAR(100) NOT NULL,
            departure_time DATETIME NOT NULL,
            arrival_time DATETIME NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            total_seats INT NOT NULL DEFAULT 40
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            bus_id INT NOT NULL,
            passenger VARCHAR(120) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            seats INT NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bus_id) REFERENCES buses(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM buses")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO buses
            (operator, source, destination, departure_time,
             arrival_time, price, total_seats)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [
            (
                "GoBus Express", "Hyderabad", "Vijayawada",
                "2026-12-01 08:00:00", "2026-12-01 14:00:00",
                650, 40
            ),
            (
                "GoBus Travels", "Hyderabad", "Bengaluru",
                "2026-12-01 21:00:00", "2026-12-02 07:00:00",
                950, 36
            ),
            (
                "GoBus Superfast", "Vijayawada", "Hyderabad",
                "2026-12-01 09:30:00", "2026-12-01 15:30:00",
                600, 40
            )
        ])

    conn.commit()
    cursor.close()
    conn.close()