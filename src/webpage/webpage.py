import jwt
from src.common.errors import ServerException, NotFoundException
from src.database.database import Database
import pymysql


class Webpage:

    def __init__(self, title: str = None, url: str = None, pagerank_score: int = -1, keywords: tuple = tuple()):
        self.title = title
        self.keywords = keywords
        self.pagerank_score = pagerank_score
        self.url = url

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "keywords": self.keywords,
            "pagerank_score": self.pagerank_score
        }

    def find(options: dict = {
        "limit": 10,
        "start": 0,
        "sort_pagerank_score": "DESC"
    }):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = "SELECT * FROM page_information pi JOIN pagerank p ON pi.id_page = p.page_id ORDER BY pagerank_score {}  LIMIT %s OFFSET %s".format(options["sort_pagerank_score"])

        cursor.execute(query, (options["limit"], options["start"]))

        webpages = cursor.fetchall()

        def mapper(page):
            return Webpage(title=page.get("title"), url=page.get("url"), pagerank_score=page.get("pagerank_score"), keywords=page.get("keywords").split(","))

        webpages = list(map(mapper, webpages))

        query = "SELECT COUNT(*) as total FROM page_information pi JOIN pagerank p ON pi.id_page = p.page_id "
        
        cursor.execute(query)

        total = cursor.fetchall()[0].get("total")

        return webpages, total
