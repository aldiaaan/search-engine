from flask import Blueprint, request, jsonify
from functools import wraps
from src.auth import Auth
from src.account import account
from src.common.errors import ServerException
from src.overall_ranking.similarity import get_all_similarity_for_api
from src.sitemap import Sitemap

bp_sitemap = Blueprint("sitemap", __name__)

@bp_sitemap.route("/3d", methods=["GET"])
def get_sitemap():
    args = {
        "limit": int(request.args.get("limit") or 10),
        "start": int(request.args.get("start") or 0),
        "query": request.args.get("query") or "",
        "countries": request.args.getlist("countries[]"),
        "sort_pagerank_score": request.args.get("sort_pagerank_score") or "DESC"
    }

    sitemap = Sitemap(args)

    return sitemap.to_3d()
