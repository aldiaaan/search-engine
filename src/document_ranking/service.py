from src.document_ranking.tf_idf import run_background_service
import os
from src.indexing.inverted_index import Indexer
from src.database.database import Database

class DocumentRankingService:
  def __init__(self, algorithm, is_aborted):
    def noop():
      return
    self.is_aborted = is_aborted or noop 
    self.algorithm = algorithm

  def run(self, options = dict()):
    if self.algorithm == 'tfidf':
      run_background_service(self.is_aborted)
    if self.algorithm == 'inverted-indexer':
      
      status = "reindex"
      useGST = options.get('use_gst') or str(os.getenv("INDEXER_USE_GST"))
      barrelMode = str(os.getenv("INDEXER_BARREL_STORE"))
      db = Database()
      idx = Indexer(db, status, useGST, barrelMode)
      if self.is_aborted():
        return
      dump = idx.getRepositoryDump()
      if self.is_aborted():
        return
      idx.generateIndex(dump)
      if self.is_aborted():
        return
      idx.sortHitlists()
      if self.is_aborted():
        return
      idx.storeIndex()
