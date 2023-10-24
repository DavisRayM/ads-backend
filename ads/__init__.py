"""
Backend server implementation for the Automated Diagnosis System
"""
__version__ = "0.0.1"

import os
from flask import Flask


from typing import Any, Optional, Mapping


def create_app(test_config: Optional[Mapping[str, Any]] = None):
    """
    Flask application factory
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")

    if not test_config:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/healthz")
    def health_check():
        return "200"

    return app
