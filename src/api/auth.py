from flask import Blueprint, request, jsonify
from src.auth import Auth
from src.common.errors import ServerException
from flask_cors import CORS, cross_origin

bp_auth = Blueprint("auth", __name__)


@bp_auth.route("/login", methods=["POST"])
@cross_origin()
def login():
    payload = request.get_json()
    
    try:
        token = Auth.create_auth_token(
            email=payload["email"], password=payload["password"])
        return jsonify({"data": {"token": token}}), 200
    except ServerException as e:
        return jsonify(e.to_json()), e.code
