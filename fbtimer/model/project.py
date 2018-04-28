from fbtimer.model import BaseModel


class Project(BaseModel):

    def __str__(self):
        return self.raw_data.get('title')

    @property
    def client_id(self):
        return self.raw_data.get('client_id')

    @property
    def services(self):
        return [Service(a) for a in self.raw_data.get('services')]


class Service(BaseModel):

    def __str__(self):
        return self.raw_data.get('name')
