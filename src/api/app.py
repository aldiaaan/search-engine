from flask import Flask, render_template, request, Response
import os
from flask_cors import CORS


def run():
    app = Flask(__name__)

    
    CORS(app)
            
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

    

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
