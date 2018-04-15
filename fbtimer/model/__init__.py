

class BaseModel:

    def __init__(self, raw_data):
        self.raw_data = raw_data

    @property
    def id(self):
        return self.raw_data.get('id', False)
