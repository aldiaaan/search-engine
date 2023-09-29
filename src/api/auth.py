from flask import Blueprint, request, jsonify
from src.auth import Auth
from src.common.errors import ServerException

bp_auth = Blueprint("auth", __name__)


@bp_auth.route("/login", methods=["POST"])
def create_new_account():
    payload = request.get_json()
    try:
        token = Auth.create_auth_token(
            email=payload["email"], password=payload["password"])
        return jsonify({"token": token}), 200
    except ServerException as e:
        return jsonify(e.to_json()), e.code
