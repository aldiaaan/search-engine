#! /opt/rh/rh-python38/root/usr/bin/python

import logging
import sys
import os

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/se2")
import flask
from dotenv import load_dotenv
from src.api.app import run
from src.database.database import Database



load_dotenv(dotenv_path="/var/www/html/se2/.env")

db = Database()
db.create_tables()
application = run()