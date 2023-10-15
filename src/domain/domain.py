import jwt
from src.common.errors import ServerException, NotFoundException
from src.database.database import Database
import pymysql
from subprocess import run
import json
import re
import requests
import geoip2.database
import os

geoip2_handle = geoip2.database.Reader(os.path.join(os.path.dirname(__file__), "geolite.mmdb"))


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
    
    def domain_name_for_country(domain: str):
        splitted_domain = domain.split(".")
        try:
            response = requests.get("http://" + domain, stream=True)
        except Exception as e:
            print(e)
        
        try:
            response = requests.get("https://" + domain, stream=True)
        except Exception as e:
            print(e)

        ip, _ = response.raw._fp.fp.raw._sock.getpeername()
        country = geoip2_handle.country(ip).registered_country.iso_code
        return country


    def find(options: dict = {
        "limit": 10,
        "start": 0,
        "query": "",
        "sort_total_pages": "DESC",
        "with_country": False
    }):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = """SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(url, "/", 3), "://", -1), "/", 1), "?", 1), "#", 1)  AS name, COUNT(*) AS total_pages FROM page_information pi2 GROUP BY name  HAVING name LIKE '{}'  ORDER BY total_pages {}  LIMIT {} OFFSET {}""".format("%" + options.get("query") + "%", options.get("sort_total_pages"), options["limit"], options["start"])
        cursor.execute(query)
        domains = cursor.fetchall()
        def mapper(row):
            
            if (options.get("with_country")):               
                country = Domain.domain_name_for_country(row.get('name'))

            return Domain(name=row.get("name"), country=country, total_pages=row.get("total_pages"))

        query = """SELECT COUNT(*) OVER () AS total,  SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(url, "/", 3), "://", -1), "/", 1), "?", 1), "#", 1)  AS name, COUNT(*) AS total_pages FROM page_information pi2 group by name  HAVING name LIKE '{}'""".format("%" + options.get("query") + "%")
        
        cursor.execute(query)
        x = cursor.fetchall()
        total = x[0].get("total") if len(x) != 0 else 0

        return list(map(mapper, domains)), total