import jwt
from src.common.errors import ServerException, NotFoundException
from src.database.database import Database
import pymysql

class Webpage:

    def __init__(self, country='UNKNOWN', id = 0, total_words: int = 0, title: str = None, url: str = None, pagerank_score: int = -1, keywords: tuple = tuple()):
        self.title = title
        self.id = id
        self.keywords = keywords
        self.country = country
        self.pagerank_score = pagerank_score
        self.url = url
        self.total_words = total_words

    def to_dict(self):
        return {
            "total_words": self.total_words,
            "title": self.title,
            "url": self.url,
            "keywords": self.keywords,
            "pagerank_score": self.pagerank_score,
            "id": self.id,
            "country": self.country
        }
    
    # get total size of all crawled webpages in byte(s)
    def get_total_size():
        db = Database()
        connection = db.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = "SELECT SUM(size_bytes) as total FROM page_information pi2 "
        cursor.execute(query)
        
        size = int(cursor.fetchall()[0].get("total"))

        return size

    def find(options: dict = {
        "limit": 10,
        "start": 0,
        "sort_pagerank_score": "DESC",
        "query": ""
    }):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = """SELECT *, COUNT(*) as total_words FROM page_information pi left join tfidf_word tw on tw.page_id = pi.id_page JOIN pagerank p ON pi.id_page = p.page_id WHERE pi.url LIKE '{}' {} GROUP BY pi.url  ORDER BY pagerank_score {}  LIMIT {} OFFSET {}""".format("%" + options["query"] + "%", "AND country IN ({})".format(','.join(list(map(lambda x: "'{}'".format(x), options.get('countries') or [])))) if len(options.get('countries') or []) > 0 else '', options["sort_pagerank_score"], options["limit"], options["start"])
        cursor.execute(query)
        
        webpages = cursor.fetchall()

        def mapper(page):
            return Webpage(country=page.get('country'), id=page.get('id_page'), title=page.get("title"), url=page.get("url"), pagerank_score=page.get("pagerank_score"), keywords=[], total_words=page.get("total_words"))

        webpages = list(map(mapper, webpages))

        query = "SELECT COUNT(*) as total FROM page_information pi WHERE pi.url LIKE '{}' {}".format("%" + options.get("query") + "%", "AND country IN ({})".format(','.join(list(map(lambda x: "'{}'".format(x), options.get('countries') or [])))) if len(options.get('countries') or []) > 0 else '')

        cursor.execute(query)
        result = cursor.fetchall()

        total = result[0].get("total") if len(result) != 0 else 0

        query = "SELECT COUNT(*) as total, country as value FROM page_information pi WHERE pi.url LIKE '{}' GROUP BY country".format("%" + options.get("query") + "%")

        cursor.execute(query)
        result = cursor.fetchall()

        countries = result


        return webpages, total, countries
