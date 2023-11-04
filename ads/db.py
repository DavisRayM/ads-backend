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


def drop_db():
    """
    Drops all application tables
    """
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("DROP TABLE Prediction")
        cur.execute("DROP TABLE Result")
        cur.execute("DROP TABLE AppUser")
        conn.commit()


@click.command("init-db")
def init_db_command():
    """Runs application migrations"""
    init_db()
    click.echo("Initialized the database")


def add_prediction(user_id: int, file_path: str, result_id: str = ""):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO Prediction(user_id, file_path, uploaded_on, status, result_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, file_path, datetime.now().isoformat(), "pending", result_id),
        )
        conn.commit()


class User:
    username: str
    id: int
    hashed_password: str

    def __str__(self) -> str:
        return f"{self.id}: {self.username}"

    @classmethod
    def create(cls, username, password):
        password = generate_password_hash(password)
        conn = get_db()

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO AppUser (username, password) VALUES (%s, %s)",
                (username, password),
            )
            conn.commit()

    @classmethod
    def get(cls, username=None, id=None):
        conn = get_db()
        with conn.cursor() as cur:
            if username is not None:
                cur.execute("SELECT * FROM AppUser WHERE username = %s", (username,))
            else:
                cur.execute("SELECT * FROM AppUser WHERE id = %s", (id,))

            row = cur.fetchone()
            if row is not None:
                user = User()
                user.id = row[0]
                user.username = row[1]
                user.hashed_password = row[2]
                return user
            else:
                return None
