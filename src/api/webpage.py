from flask import Blueprint, request, jsonify
from src.auth import Auth
from src.common.errors import ServerException
from src.webpage import Webpage
import math

bp_webpage = Blueprint("webpage", __name__)


@bp_webpage.route("/", methods=["GET"])
def get_webpages():
    webpages, total, countries = Webpage.find({
        "limit": int(request.args.get("limit") or 10),
        "start": int(request.args.get("start") or 0),
        "query": request.args.get("query") or "",
        "countries": request.args.getlist("countries[]"),
        "sort_pagerank_score": request.args.get("sort_pagerank_score") or "DESC"
    })
    return {
        "data": list(map(lambda x: x.to_dict(), webpages)),
        "pagination": {
            "total": total,
            "size": Webpage.get_total_size(),
            "pages": math.ceil(total / int(request.args.get("limit") or 10)),
            "current_page": math.floor(int(request.args.get("start") or 0) / int(request.args.get("limit") or 10))
        },
        "facets": {
            "countries": countries
        }
    }
