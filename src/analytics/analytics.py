
from src.common.errors import ServerException, NotFoundException
from src.database.database import Database
import pymysql

class Analytics:
  def __init__(self):
    return
  
  def save_query_log(query: str = "", ip: str = None, ua: str = None):
    try:
      db = Database()
      connection = db.connect()
      cursor = connection.cursor(pymysql.cursors.DictCursor)

      query = "INSERT INTO search_log (query, ip, ua) VALUES ('{}', '{}', '{}')".format(query, ip, ua)

      print(query)

      cursor.execute(query)

      return True
    except Exception as e:
      raise e