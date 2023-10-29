from src.document_ranking.tf_idf import run_background_service
import os
from src.indexing.inverted_index import Indexer
from src.database.database import Database

class DocumentRankingService:
  def __init__(self, algorithm):
    self.algorithm = algorithm

  def run(self, options = dict()):
    if self.algorithm == 'tfidf':
      run_background_service()
    if self.algorithm == 'inverted-indexer':
      
      status = "reindex"
      useGST = options.get('use_gst') or str(os.getenv("INDEXER_USE_GST"))
      barrelMode = str(os.getenv("INDEXER_BARREL_STORE"))
      db = Database()
      idx = Indexer(db, status, useGST, barrelMode)
      dump = idx.getRepositoryDump()
      idx.generateIndex(dump)
      idx.sortHitlists()
      idx.storeIndex()
