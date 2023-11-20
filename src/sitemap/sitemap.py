from src.overall_ranking.similarity import get_all_similarity_for_api
from src.database.database import Database 
import pymysql
from functools import reduce

class Sitemap:

    def ping():
        return "pong"

    def __init__(self, options: dict = dict()):
        self.query = options.get('query')
        self.countries = options.get('countries')

    def to_3d(self):
        sites, total = get_all_similarity_for_api(
            keyword=self.query, sort='similarity')
        
        db = Database()
        connection = db.connect()
        countries_filter = 'AND pi.country IN {}'.format("({})".format(','.join(list(map(lambda x: "'{}'".format(x), self.countries)))))
        id_filter = "({})".format(','.join(list(map(lambda x: "'{}'".format(x.get('id_page')), sites))))
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = "SELECT pi.url AS source, pl.outgoing_link AS target FROM page_linking pl JOIN page_information pi ON pl.page_id = pi.id_page WHERE page_id IN {} {}".format(id_filter, countries_filter if len(self.countries) > 0 is not None else '')
        cursor.execute(query)
        linking = cursor.fetchall()

        nodes = set()

        for obj in linking:
            nodes.add(obj.get('source'))
            nodes.add(obj.get('target'))

        result_group = list(map(lambda x: x.get('url'), sites))

        return {
            'links': linking,
            'total': len(nodes),
            'nodes': list(map(lambda x: {'id': x, 'group': 2 if x in result_group else 1},list(nodes)))
        }
