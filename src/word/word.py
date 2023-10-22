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
  def get_overall_wordclouds():
    db = Database()
    connection = db.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "select * from tfidf_word"
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


  def __init__(self):
    pass