-- Clinic Booking schema. Safe to run more than once (IF NOT EXISTS).
-- After a schema change: delete the database file and run init-db again.

CREATE TABLE IF NOT EXISTS doctors (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    specialty    TEXT    NOT NULL,
    slot_minutes INTEGER NOT NULL CHECK (slot_minutes IN (10, 15, 20, 30, 45, 60)),
    active       INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS doctor_hours (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id  INTEGER NOT NULL REFERENCES doctors (id),
    weekday    INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    start_time TEXT    NOT NULL,
    end_time   TEXT    NOT NULL,
    UNIQUE (doctor_id, weekday)
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('admin', 'receptionist', 'doctor')),
    doctor_id     INTEGER REFERENCES doctors (id),
    active        INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS patients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    phone         TEXT NOT NULL UNIQUE,
    date_of_birth TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id     INTEGER NOT NULL REFERENCES doctors (id),
    patient_id    INTEGER NOT NULL REFERENCES patients (id),
    start_at      TEXT    NOT NULL,
    end_at        TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'booked'
                  CHECK (status IN ('booked', 'cancelled', 'completed', 'no_show')),
    cancel_reason TEXT,
    created_by    INTEGER NOT NULL REFERENCES users (id),
    created_at    TEXT    NOT NULL,
    updated_at    TEXT    NOT NULL
);

-- Database guard against double booking: one non-cancelled appointment per doctor and start time.
CREATE UNIQUE INDEX IF NOT EXISTS idx_appointments_doctor_start_active
    ON appointments (doctor_id, start_at)
    WHERE status != 'cancelled';
