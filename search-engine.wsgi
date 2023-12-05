#! /opt/rh/rh-python38/root/usr/bin/python

import logging
import sys
import os

logging.basicConfig(stream=sys.stderr)
# sys.path.insert(0, "/var/www/html/search-engine")
sys.path.insert(0, "C:\\Users\\Aldian\\Desktop\\projects\\search-engine")
# sys.path.insert(0, "C:\\Users\\Aldian\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages\\cryptography\\hazmat\\bindings\\_rust.pyd")

# sys.stdout = open('output.logs', 'w')
from src.api.app import run
from src.database.database import Database
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join("C:\\Users\\Aldian\\Desktop\\projects\\search-engine", '.env'))


# raise Exception(os.getenv('API_PORT'))

db = Database()
db.create_tables()
application = run(os.getenv('API_PORT'))
