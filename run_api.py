from src.database.database import Database
from src.api.app import run
from src.domain.domain import Domain
import os
from dotenv import load_dotenv
from src.bootstrap import collect_domains
import sys

def warmup():
    print('warming up...')

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()
    warmup()
    # collect_domains()

    api_port = os.getenv("API_PORT")
    application = run()
    application.run(port=api_port)
