from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
from src.database.database import Database
import pymysql
import io
from wordcloud import STOPWORDS
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib


matplotlib.use('Agg')


class Word:

  def __init__(self, tfidf_score: int = 0, value: str = "", id: str = "", frequency: int = 0):
    self.tfidf_score = tfidf_score
    self.value = value
    self.id = id
    self.frequency = frequency

  def to_dict(self):
    return {
      "tfidf_score": self.tfidf_score,
      "value": self.value,
      "id": self.id,
      "frequency": self.frequency
    }

  def get_overall_wordclouds(options = dict()):

    url = options.get('url')

    db = Database()
    connection = db.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if url is None:      
      sql = "select * from tfidf_word"
      query = cursor.execute(sql)

      words = cursor.fetchall()
      

      wordcloud = WordCloud(background_color="white").generate(" ".join([x.get('word') for x in words]))
    else:
      sql = "select * from tfidf_word tw join page_information pi where url = {}".format(url)
      
      query = cursor.execute(sql)

      words = cursor.fetchall()
      

      wordcloud = WordCloud(background_color="white").generate(" ".join([x.get('word') for x in words]))
# Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")    
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=300)
    return buffer
  
  def occurrences(options: dict()):
    
    limit = options.get('limit') or 25
    start = options.get('start') or 0
    word = options.get('word') or ''
    sort_frequency = options.get('sort_frequency') or 'DESC'

    db = Database()
    connection = db.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM tfidf_word tw join page_information pi2 on pi2.id_page = tw.page_id  where word = '{}' limit {}, {}".format(word, start, limit)
    print(sql)
    cursor.execute(sql)

    words = cursor.fetchall()

    sql = "SELECT *, COUNT(*) as total FROM tfidf_word tw join page_information pi2 on pi2.id_page = tw.page_id  where word = '{}'".format(word)
   
    cursor.execute(sql)

    total = cursor.fetchall()[0].get('total')
    
    def mapper(x):
      return {
        "tfidf_score": x.get('tfidf_score'),
        "id": x.get('page_id'),
        "value": x.get('word'),
        "url": x.get('url'),
        "title": x.get('title'),
        "description": x.get('description')
      } 

    return list(map(mapper, words)), total
  
  def find(options: dict()):

    limit = options.get('limit') or 25
    start = options.get('start') or 0
    query = options.get('query') or ''
    sort_frequency = options.get('sort_frequency') or 'DESC'

    db = Database()
    connection = db.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "select *, count(*) as frequency from tfidf_word where word like '%{}%' group by word order by frequency {} LIMIT {}, {}".format(query, sort_frequency, start, limit)

    print(sql)
    cursor.execute(sql)

    words = cursor.fetchall()

    sql = "select count(distinct word) as total from tfidf_word where word like '%{}%'".format(query)
   

    print(sql)
    cursor.execute(sql)

    total = cursor.fetchall()[0].get('total')

    return words, total
