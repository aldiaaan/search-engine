from flask import Blueprint, request, jsonify, make_response
from functools import wraps
from src.auth import Auth
from src.account import account
from src.word import Word
from src.common.errors import ServerException
from src.word import Word
import math

bp_words = Blueprint("words", __name__)

    

@bp_words.route("/wordclouds", methods=["GET"])
def get_overall_wordclouds():
  buffered_image = Word.get_overall_wordclouds()
  response = make_response(buffered_image.getvalue())
  response.mimetype = "image/png"
  return response


@bp_words.route("/", methods=["GET"])
def get_words():
    start = int(request.args.get('start') or 0)
    limit = int(request.args.get('limit') or 20)
    query = request.args.get('query') or ''

    words, total = Word.find(options={
            'start': start,
            'limit': limit,
            'query': query
        })

    return {
        'data': words,
        'pagination': {
            'total': total,
            'pages': math.ceil(total / limit),
            'limit': limit
        },
        'message': 'ok'
    }, 200
