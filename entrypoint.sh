#!/bin/bash
python3 main.py db upgrade
flask run --host=0.0.0.0 --port 5000