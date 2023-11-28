from dotenv import load_dotenv
from src.page_ranking.page_rank import run_background_service, run_background_service_threaded
from src.database.database import Database

if __name__ == "__main__":
    load_dotenv()
    db = Database()
    db.create_tables()

    run_background_service()
    # run_background_service_threaded()
