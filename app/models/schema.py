from app.models.database import Database


USERS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role ENUM('student', 'organizer', 'admin') NOT NULL DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

EVENTS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        genre VARCHAR(100),
        date DATE NOT NULL,
        time VARCHAR(20),
        location VARCHAR(200),
        capacity INT DEFAULT 100,
        description TEXT,
        organizer_id INT NOT NULL,
        status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE CASCADE
    )
"""

REGISTRATIONS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS registrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT NOT NULL,
        student_id INT NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        attended BOOLEAN DEFAULT FALSE,
        UNIQUE KEY unique_registration (event_id, student_id),
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
    )
"""

CATEGORIES_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

ANNOUNCEMENTS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS announcements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
    )
"""

NOTIFICATIONS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        message VARCHAR(255) NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
"""

DEFAULT_CATEGORIES = ("Technical", "Cultural", "Sports", "Workshop", "Entertainment")


def _column_exists(db, table_name, column_name):
    result = db.fetch_one("""
        SELECT COUNT(*) AS cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
    """, (table_name, column_name))
    return bool(result and result["cnt"])


def _add_column(db, table_name, column_name, definition):
    if not _column_exists(db, table_name, column_name):
        db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def _seed_categories(db):
    for category in DEFAULT_CATEGORIES:
        db.execute("INSERT IGNORE INTO categories (name) VALUES (%s)", (category,))


def _upgrade_existing_tables(db):
    _add_column(db, "users", "phone", "VARCHAR(30)")
    _add_column(db, "users", "college", "VARCHAR(150)")
    _add_column(db, "users", "reset_token", "VARCHAR(100)")

    _add_column(db, "events", "category_id", "INT")
    _add_column(
        db,
        "events",
        "event_status",
        "ENUM('upcoming', 'ongoing', 'completed', 'cancelled') DEFAULT 'upcoming'",
    )
    db.execute(
        "ALTER TABLE events MODIFY status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending'"
    )
    db.execute(
        "ALTER TABLE events MODIFY event_status "
        "ENUM('upcoming', 'ongoing', 'completed', 'cancelled') DEFAULT 'upcoming'"
    )

    _add_column(
        db,
        "registrations",
        "status",
        "ENUM('pending', 'selected', 'waitlisted', 'rejected', 'cancelled') DEFAULT 'selected'",
    )
    _add_column(db, "registrations", "certificate_available", "BOOLEAN DEFAULT FALSE")
    db.execute(
        "ALTER TABLE registrations MODIFY status "
        "ENUM('pending', 'selected', 'waitlisted', 'rejected', 'cancelled') DEFAULT 'selected'"
    )


def create_tables():
    db = Database()
    if not db.is_connected:
        print("Skipping table creation: no DB connection.")
        return

    db.execute(USERS_TABLE_SQL)
    db.execute(CATEGORIES_TABLE_SQL)
    db.execute(EVENTS_TABLE_SQL)
    db.execute(REGISTRATIONS_TABLE_SQL)
    db.execute(ANNOUNCEMENTS_TABLE_SQL)
    db.execute(NOTIFICATIONS_TABLE_SQL)
    _upgrade_existing_tables(db)
    _seed_categories(db)
    db.close()
