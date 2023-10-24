"""
Module contains MongoDB helper functions
"""
from flask import current_app, g
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy


def get_db():
    """
    Retrieves existing connection to MongoDB or creates one if none is
    present
    """
    conn = getattr(g, "_db", None)
    if conn is None:
        conn = g._db = PyMongo(current_app, serverSelectionTimeoutMS=10000).db

    return conn


db = LocalProxy(get_db)
