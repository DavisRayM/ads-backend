"""
Module contains MongoDB helper functions
"""
from typing import Any, Dict
from flask import current_app, g
from flask_pymongo import PyMongo


def get_db():
    """
    Retrieves existing connection to MongoDB or creates one if none is
    present
    """
    conn = getattr(g, "_db", None)
    if conn is None:
        conn = g._db = PyMongo(current_app, serverSelectionTimeoutMS=10000).db

    return conn


def get_user(username: str) -> Dict[str, Any]:
    return get_db().users.find_one({"username": username})
