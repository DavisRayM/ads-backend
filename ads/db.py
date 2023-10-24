"""
Module contains MongoDB helper functions
"""
from datetime import datetime
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


def add_prediction(user: str, file_path: str, result_id: str = ""):
    prediction_doc = {
        "username": user,
        "file_path": file_path,
        "uploaded_on": datetime.now().isoformat(),
        "status": "pending",
        "result_id": result_id,
    }
    return get_db().predictions.insert_one(prediction_doc)
