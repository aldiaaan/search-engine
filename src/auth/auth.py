import jwt
from src.account import Account
from src.common.errors import ServerException, NotFoundException
import bcrypt


class Auth:
    def verify(token: str):     
        try:              
            decoded = jwt.decode(token, "secret", algorithms=["HS256"])       
            account = Account(email=decoded.get("email")).get()
            if account is None:
                raise Exception("account not found")
            return account
        except Exception as e:
            return None
    
    def create_auth_token(email: str, password: str):

        account = Account(email=email, password=password).get()

        if account is None:
            raise NotFoundException("Account not found")

        is_authenticated = bcrypt.checkpw(password.encode(
            "utf-8"), account.password.encode('utf-8'))

        token = jwt.encode({"email": account.email}, "secret", algorithm="HS256")

        if is_authenticated:
            return token
        
        raise ServerException("Invalid credentials provided", 403)

    def __init__(self):
        return
