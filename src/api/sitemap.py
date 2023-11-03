from flask import Blueprint, request, jsonify
from functools import wraps
from src.auth import Auth
from src.account import account
from src.common.errors import ServerException
from src.overall_ranking.similarity import get_all_similarity_for_api

bp_sitemap = Blueprint("sitemap", __name__)

@bp_sitemap.route("/3d", methods=["GET"])
def get_sitemap():
    payload = request.get_json()
    query = request.args.get('query')
    country = request.args.get('country')
    sites = get_all_similarity_for_api(query)
    try:
        return jsonify({"data": sites}), 200
    except Exception as e:
        return {"msg": "something went wrong"}
