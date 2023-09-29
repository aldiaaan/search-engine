import jwt
from src.account import Account
from src.common.errors import ServerException
import bcrypt


class Auth:
    def create_auth_token(email: str, password: str):

        account = Account(email=email, password=password).get()

        is_authenticated = bcrypt.checkpw(password.encode(
            "utf-8"), account.password.encode('utf-8'))

        token = jwt.encode({"email": account.email}, "secret", algorithm="HS256")

        if is_authenticated:
            return token
        
        raise ServerException("Invalid credentials", 403)

    def __init__(self):
        return
