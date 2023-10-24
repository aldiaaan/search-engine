from src.document_ranking.tf_idf import run_background_service

class DocumentRankingService:
  def __init__(self, algorithm):
    self.algorith = algorithm

  def run(self):
    if self.algorithm == 'tfidf':
      run_background_service()
