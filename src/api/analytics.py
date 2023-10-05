from flask import Blueprint, request, jsonify
from src.common.errors import ServerException
from src.analytics import Analytics
import math

bp_analytics = Blueprint("analytics", __name__)


@bp_analytics.route("/events/search", methods=["POST"])
def save_query():
    payload = request.get_json()
    Analytics.save_query_log(query=payload.get("query"), ip=request.remote_addr, ua=request.headers.get('User-Agent'))
    return jsonify({
        "message": "ok"
    }), 200
