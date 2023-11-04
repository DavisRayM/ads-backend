from os import environ
import secrets


class Settings(object):
    """
    Base class for settings; should contain all common attributes
    """

    # For production pick an actual key
    SECRET_KEY = environ.get("SECRET_KEY", secrets.token_urlsafe(16))

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    CELERY = {
        "broker_url": "redis://redis",
        "result_backend": "redis://redis",
        "task_ignore_result": False,
    }

    # More info: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    DATABASE_DSN = environ.get(
        "DATABASE_DSN",
        "host=localhost port=5432 dbname=ads_backend user=dev password=dev",
    )
