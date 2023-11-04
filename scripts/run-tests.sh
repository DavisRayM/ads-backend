#!/bin/bash

PYTHONPATH=. flask --app ads init-db --drop 
PYTHONPATH=. pytest
