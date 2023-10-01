import jwt
from src.common.errors import ServerException, NotFoundException
from src.database.database import Database
import pymysql
from subprocess import run
import json
import re


class Domain:

    def __init__(self, name: str = None, country: str = "UNKNOWN", total_pages: int = 0):
        self.name = name
        self.country = country
        self.total_pages = total_pages

    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "total_pages": self.total_pages
        }

    def find(options: dict = {
        "limit": 10,
        "start": 0,
        "sort_total_pages": "DESC"
    }):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = """SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(url, "/", 3), "://", -1), "/", 1), "?", 1), "#", 1)  AS name, COUNT(*) AS total_pages FROM page_information pi2 GROUP BY name ORDER BY total_pages {} LIMIT %s OFFSET %s""".format(options.get("sort_total_pages"))
        cursor.execute(query, (options["limit"], options["start"]))

        domains = cursor.fetchall()

        def mapper(row):
            whois = run("whois {}".format(row.get("name")),
                       capture_output=True, shell=True, text=True)

            country = "UNKNOWN"       
            countries = re.findall("(?<=Registrant Country: ).\S*", whois.stdout)
            if len(countries) != 0:
                country = countries[0]
            return Domain(name=row.get("name"), country=country, total_pages=row.get("total_pages"))

        query = """SELECT COUNT(*) OVER () AS total,  SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(url, "/", 3), "://", -1), "/", 1), "?", 1), "#", 1)  AS name, COUNT(*) AS total_pages FROM page_information pi2 group by name"""
        cursor.execute(query)

        total = cursor.fetchall()[0].get("total")

        return list(map(mapper, domains)), total
