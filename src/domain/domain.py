import jwt
from src.common.errors import ServerException, NotFoundException
from src.database.database import Database
import pymysql
import multiprocessing 
from subprocess import run
from cachetools import cached, LRUCache, TTLCache
import json
import re
import requests
import geoip2.database
import os

geoip2_handle = geoip2.database.Reader(os.path.join(os.path.dirname(__file__), "geolite.mmdb"))

def worker(domain):
    return {"name": domain.name, "country": Domain.domain_name_for_country(domain.name)}

class Domain:

    def __init__(self, name: str = None, country: str = "UNKNOWN", total_pages: int = 0):
        self.name = name
        self.country = country
        self.total_pages = total_pages


    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_stats():
        
        domains, total = Domain.find({
            "limit": 18446744073709551615,
            "start": 0,
            "query": "",
            "sort_total_pages": "DESC",
            "with_country": False
        })

        with multiprocessing.Pool() as pool: 
            results = pool.map(worker, domains) 

        stats = dict()

        for domain in results:
            if stats.get(domain.get('country')) is None:
                stats[domain.get('country')] = [domain.get('name')]
            else:
                stats[domain.get('country')].append(domain.get('name'))
        
        return stats
            

    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "total_pages": self.total_pages
        }
    
    def domain_name_for_country(domain: str):
        splitted_domain = domain.split(".")
        country = "UNKNOWN"
        try:
            response = requests.get("http://" + domain, stream=True)
        except Exception as e:
            print(e)
        
        try:
            response = requests.get("https://" + domain, stream=True)
        except Exception as e:
            return "UNKNOWN"

        ip, _ = response.raw._fp.fp.raw._sock.getpeername()
        country = geoip2_handle.country(ip).registered_country.iso_code
        return country
    
    def save(self):
        country = self.country
        name = self.name

        if not name or not country:
            raise Exception("[Domain::save] name or country cannot be undefined")
        
        db = Database()
        connection = db.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        query = """SELECT * FROM domains where name = '{}'""".format(name)

        cursor.execute(query)

        if len(cursor.fetchall()) > 0:
            raise Exception('[Domain::save] domain {} has already been registered in database'.format(name))

        query = """INSERT INTO domains (name, country) VALUES ('{}', '{}')""".format(name, country)

        print("[Domain::save] {} with country {} saved!".format(name, country))

        cursor.execute(query)

        


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
                
            country = Domain.domain_name_for_country(row.get('name')) if options.get('with_country') else 'UNKNOWN'

            return Domain(name=row.get("name"), country=country, total_pages=row.get("total_pages"))

        query = """SELECT COUNT(*) OVER () AS total,  SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(url, "/", 3), "://", -1), "/", 1), "?", 1), "#", 1)  AS name, COUNT(*) AS total_pages FROM page_information pi2 group by name  HAVING name LIKE '{}'""".format("%" + options.get("query") + "%")
        
        cursor.execute(query)
        x = cursor.fetchall()
        total = x[0].get("total") if len(x) != 0 else 0

        return list(map(mapper, domains)), total