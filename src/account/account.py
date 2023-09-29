from src.database.database import Database
from enum import Enum
from src.common.errors import NotFoundException
import bcrypt
import pymysql.cursors

class Account:

  ROLE_STAFF = "staff"

  def __init__(self, email: str = None, password: str = None, role: str = None, id: str = None,  first_name: str = None, last_name: str = None):
    self.id = id
    self.email = email
    self.db = Database()
    self.first_name = first_name
    self.last_name = last_name
    self.role = role
    self.password = password

  def to_json(self):
    return {
      "id": self.id,
      "first_name": self.first_name,
      "full_name": "{} {}".format(self.first_name, self.last_name),
      "last_name": self.last_name,
      "role": self.role,
      "email": self.email
    }

  def save(self):
    connection = self.db.connect()
    cursor = connection.cursor()
    query = "INSERT INTO accounts (email, first_name, last_name, password, role) VALUES (%s, %s, %s, %s, %s)"

    cursor.execute(query, (self.email, self.first_name, self.last_name, bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt()), self.role))

    self.id = cursor.lastrowid

    return self
  
  def get(self):

    connection = self.db.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    query = "SELECT * FROM accounts WHERE id = %s OR email = %s"

    cursor.execute(query, (self.id, self.email))

    accounts = cursor.fetchall() 

    if len(accounts) == 0:
      return None
    
    account = accounts[0]

    return Account(password=account["password"], first_name=account["first_name"], last_name=account["last_name"], role=account["role"], email=account["email"])