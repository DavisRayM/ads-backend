#!/bin/bash

pip-compile -o base.pip pyproject.toml
pip-compile -o dev.pip --extra test,dev pyproject.toml
