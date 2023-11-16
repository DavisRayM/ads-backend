"""
Module contains MongoDB helper functions
"""
import os
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
@click.option(
    "--drop",
    help="Whether to drop database",
    is_flag=True,
    show_default=True,
    default=False,
)
def init_db_command(drop: bool):
    """Runs application migrations"""
    if drop:
        drop_db()
        click.echo("Dropped tables")
    init_db()
    click.echo("Initialized the database")


class Prediction:
    id: int
    user_id: int
    file_path: str
    uploaded_on: datetime
    status: str
    result_id: int

    def dict(self):
        return {
            "id": self.id,
            "uploaded_on": self.uploaded_on.isoformat(),
            "status": self.status,
        }

    def set_result(self, result_id: int):
        self.result_id = result_id
        self.status = "complete"
        self._save()

        try:
            os.remove(self.file_path)
        except OSError as e:
            current_app.logger.error(
                f"failed to delete image: {self.file_path} - {self.id}. Error: {e}"
            )

    def _save(self):
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Prediction SET file_path = ?, status = ?, result_id = ?, user_id = ?",
                (self.file_path, self.status, self.result_id, self.user_id),
            )
            conn.commit()

    @property
    def user(self):
        if self.user_id:
            return User.get(id=self.user_id)

    @classmethod
    def get(cls, id: int):
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Prediction WHERE id = %s", (id,))

            row = cur.fetchone()
            if row is not None:
                obj = Prediction()
                obj.id = row[0]
                obj.file_path = row[1]
                obj.uploaded_on = row[2]
                obj.status = row[3]
                obj.result_id = row[4]
                obj.user_id = row[5]
                return obj
            else:
                return None

    @classmethod
    def create(cls, user, file_path, result_id):
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Prediction(user_id, file_path, uploaded_on, status, result_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (user.id, file_path, datetime.now().isoformat(), "pending", result_id),
            )
            conn.commit()
            result = cur.fetchone()
            if result:
                return cls.get(id=result[0])


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
                "INSERT INTO AppUser (username, password) VALUES (%s, %s) RETURNING id",
                (username, password),
            )
            conn.commit()
            result = cur.fetchone()
            if result:
                return cls.get(id=result[0])

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
                obj = User()
                obj.id = row[0]
                obj.username = row[1]
                obj.hashed_password = row[2]
                return obj
            else:
                return None
