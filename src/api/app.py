from flask import Flask, jsonify, render_template, request, Response, send_from_directory
import os
from flask_cors import CORS
from src.exceptions import BaseException
import multiprocessing
import time
import random
import string
from src.celery.init import celery_init_app
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.abspath('../..'), '.env'))





def task():
    file = open(f'./test/{"".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))}.txt', 'a')
    print('sleeping...')
    time.sleep(200)

def run():
    app = Flask(__name__)

    app.config.from_mapping(
        CELERY=dict(
            broker_url=os.getenv('CELERY_BROKER_URL'),
            result_backend = os.getenv('CELERY_RESULT_BACKEND'),
            task_ignore_result=True,
            task_track_started=True,
        ),
    )

    app.config.from_prefixed_env()


    
    CORS(app)
    celery_init_app(app)
            
            
    from src.api.crawling import bp_crawling
    from src.api.page_ranking import bp_page_ranking
    from src.api.document_ranking import bp_document_ranking
    from src.api.overall_ranking import bp_overall_ranking
    from src.api.account import bp_account
    from src.api.auth import bp_auth
    from src.api.webpage import bp_webpage
    from src.api.domain import bp_domain
    from src.api.profile import bp_profile
    from src.api.analytics import bp_analytics
    from src.api.words import bp_words
    from src.api.sitemap import bp_sitemap

    api_version = os.getenv("API_VERSION")
    app.register_blueprint(bp_crawling, url_prefix="/api/" + api_version + "/crawling")
    app.register_blueprint(bp_words, url_prefix="/api/" + api_version + "/words")
    # app.register_blueprint(bp_profile, url_prefix="/api/" + api_version + "/profile")
    app.register_blueprint(bp_page_ranking, url_prefix="/api/" + api_version + "/page_ranking")
    app.register_blueprint(bp_document_ranking, url_prefix="/api/" + api_version + "/document_ranking")
    app.register_blueprint(bp_overall_ranking, url_prefix="/api/" + api_version + "/overall_ranking")
    app.register_blueprint(bp_account, url_prefix="/api/" + api_version + "/accounts")
    app.register_blueprint(bp_auth, url_prefix="/api/" + api_version + "/auth")
    app.register_blueprint(bp_webpage, url_prefix="/api/" + api_version + "/webpages")
    app.register_blueprint(bp_domain, url_prefix="/api/" + api_version + "/domains")
    app.register_blueprint(bp_analytics, url_prefix="/api/" + api_version + "/analytics")
    
    app.register_blueprint(bp_sitemap, url_prefix="/api/" + api_version + "/sitemap")
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, BaseException):
            return e.to_dict(), e.status
        else:
            return e
        
    app.register_error_handler(Exception, handle_exception)

    
    @app.route("/ping")
    def ping():
        p = multiprocessing.Process(target=task)
        p.daemon = True
        try:
            p.start()
            print(p.pid)
            return f"{p.pid}"
        except Exception as e:
            print(e)
            return f"{e}"
        return "PONG"

    @app.route("/")
    def index():
        # return os.path.abspath(__file__ + "/../../web_client/")
        return send_from_directory(os.path.abspath(__file__ + "/../../web_client/"), "index.html")
        # return os.path.abspath(os.path.dirname(os.path.abspath(__file__)), '..')

    @app.route("/assets/<path:path>")
    def static_proxy(path):
        # return path
        """static folder serve"""
        # file_name = path.split("/")[-1]
        return send_from_directory(os.path.abspath(__file__ + "/../../web_client/assets/"), path)

    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return jsonify(message="Resource not found"), 404
        return send_from_directory(os.path.abspath(__file__ + "/../../web_client/"), "index.html")

    return app
