class Column:
  '''Klas sa, sèvi pou kreye chak kolòn nan baz done a, olye pou se nou ki kreye kòd SQL la'''
  '''Li responsab tou, pou jenere migrasyon otomatik'''
  def __init__(self, col_type, required=False, default=None, unique=False, constraint=None, **kwargs):
    # pkey = primary_key
    # fkey = foreign_key
    self.col_type = col_type
    self.required = required
    self.default = default
    self.unique = True if constraint == 'pkey' else unique
    self.constraint = constraint
    self.model = kwargs.get('model')
    self.through_model = kwargs.get('through_model')
    self.max_length = kwargs.get('max_length')
    self._value = kwargs.get('value')
    self.name = None

    def __str__(self):
      return f"Column(type={self.col_type}, required={self.required}, default={self.default}, unique={self.unique}, constraint={self.constraint})"

    def __repr__(self):
      return self.name