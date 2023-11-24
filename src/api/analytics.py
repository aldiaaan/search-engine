from flask import Blueprint, request, jsonify
from src.common.errors import ServerException
from src.analytics import Analytics
import math

bp_analytics = Blueprint("analytics", __name__)


@bp_analytics.route("/events/search/", methods=["POST"])
def save_query():
    payload = request.get_json()
    Analytics.save_query_log(query=payload.get(
        "query"), ip=request.remote_addr, ua=request.headers.get('User-Agent'))
    return jsonify({
        "message": "ok"
    }), 200

@bp_analytics.route("/top_searched_words", methods=["GET"])
def top_10_searched_words():
    
    start = int(request.args.get('start') or 0)
    limit = int(request.args.get('limit') or 20)
    query = request.args.get('query') or ''

    logs, total = Analytics.get_searched_keywords_stats(options={
            'start': start,
            'limit': limit,
            'query': query
        })

    return {
        'data': logs,
        'pagination': {
            'total': total,
            'pages': math.ceil(total / limit),
            'limit': limit
        },
        'message': 'ok'
    }, 200

@bp_analytics.route("/search_logs", methods=["GET"])
def search_logs():

    start = int(request.args.get('start') or 0)
    limit = int(request.args.get('limit') or 20)
    query = request.args.get('query') or ''

    logs, total = Analytics.get_query_log(options={
            'start': start,
            'limit': limit,
            'query': query
        })

    return {
        'data': logs,
        'pagination': {
            'total': total,
            'pages': math.ceil(total / limit),
            'limit': limit
        },
        'message': 'ok'
    }, 200
