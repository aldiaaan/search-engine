
from src.common.errors import ServerException, NotFoundException
from src.database.database import Database
import pymysql

class Analytics:
  def __init__(self):
    return
  
  def get_searched_keywords_stats(options = dict()):
    start = options.get('start') or 0
    limit = options.get('limit') or 20
    query = options.get('query') or ''

    try:
      db = Database()
      connection = db.connect()
      cursor = connection.cursor(pymysql.cursors.DictCursor)

      sql = "select query, COUNT(*) as frequency from search_log sl group by query order by frequency desc LIMIT {}, {}".format(start, limit)

      query = cursor.execute(sql)

      words = cursor.fetchall()

      
      sql = "SELECT COUNT(*) OVER () AS total from search_log sl group by query".format(start, limit)

      query = cursor.execute(sql)

      rows = cursor.fetchall()

      if len(rows) > 0:
        total = rows[0].get('total')

      return words, total
    except Exception as e:
      raise e
  
  def get_query_log(options = dict()):
    start = options.get('start') or 0
    limit = options.get('limit') or 20
    query = options.get('query') or ''

    try:
      db = Database()
      connection = db.connect()
      cursor = connection.cursor(pymysql.cursors.DictCursor)

      sql = "SELECT * FROM search_log ORDER BY `id` DESC LIMIT {}, {}".format(start, limit)

      query = cursor.execute(sql)

      logs = cursor.fetchall()

      
      sql = "SELECT COUNT(*) as total FROM search_log".format(start, limit)

      query = cursor.execute(sql)

      rows = cursor.fetchall()

      if len(rows) > 0:
        total = rows[0].get('total')

      return logs, total
    except Exception as e:
      raise e
  
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