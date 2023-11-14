class BaseException(Exception):

  def __init__(self, args):
    self.message = args.get('message') or 'Something went wrong'
    self.code = args.get('code') or 'SERVER_EXCEPTION'
    self.status = args.get('status') or 500


  def to_dict(self):
    return {
      'code': self.code,
      'message': self.message
    }
  
class DuplicateDataException(BaseException):
  def __init__(self, name):
    super().__init__({
      'status': 401,
      'message': 'Duplicate {}'.format(name),
      'code': 'DUPLICATE_DATA_EXCEPTION'
    })
