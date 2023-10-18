from flask import Blueprint, request, jsonify
from functools import wraps
from src.auth import Auth
from src.account import account
from src.common.errors import ServerException

bp_profile = Blueprint("profile", __name__)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.headers.get("X-Auth-Token")
        account = Auth.verify(token)
        
        if account is None:
            return jsonify({
                "message": "invalid credentials or account not found"
            }), 400
        kwargs['account'] = account
        return f(*args, **kwargs)
    return wrap
    

@bp_profile.route("/me", methods=["GET"])
@login_required
def create_new_account(account):
    payload = request.get_json()
    try:
        return jsonify({"data": account.to_dict()}), 200
    except ServerException as e:
        return jsonify(e.to_json()), e.code
