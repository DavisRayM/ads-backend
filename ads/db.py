"""
Module contains MongoDB helper functions
"""
import click
import psycopg
from datetime import datetime

from flask import current_app, g
from werkzeug.security import generate_password_hash


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db() -> psycopg.Connection:
    """
    Retrieves existing connection to MongoDB or creates one if none is
    present
    """
    if "db" not in g:
        g.db = psycopg.connect(current_app.config["DATABASE_DSN"])

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    Runs the applications schemas; initialiazing the tables in the database
    """
    conn = get_db()

    with current_app.open_resource("schema.sql") as f:
        with conn.cursor() as cur:
            cur.execute(f.read().decode("utf-8"))
            conn.commit()


@click.command("init-db")
def init_db_command():
    """Runs application migrations"""
    init_db()
    click.echo("Initialized the database")


def add_user(username: str, raw_password: str):
    """
    Adds a new user to the database
    """
    password = generate_password_hash(raw_password)
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO AppUser (username, password) VALUES (%s, %s)",
            (username, password),
        )
        conn.commit()


def get_user(username: str):
    with get_db().cursor() as cur:
        cur.execute("SELECT * FROM AppUser WHERE username = %s", (username,))
        return cur.fetchone()


def add_prediction(user_id: int, file_path: str, result_id: str = ""):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO Prediction(user_id, file_path, uploaded_on, status, result_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, file_path, datetime.now().isoformat(), "pending", result_id),
        )
        conn.commit()
