from tinydb import TinyDB, Query

class DataLayer:
    def __init__(self, db_path, table_name):
        self.db = TinyDB(db_path)
        self.table = self.db.table(table_name)

    def create(self, data):
        self.table.insert(data)

    def read(self, key=None, value=None):
        if key and value:
            result = self.table.search(Query()[key] == value)
        else:
            result = self.table.all()
        return result
    
    def read_start_with(self, key=None, value=None):
        return self.table.search(Query()[key].matches (value + '_*'))

    def update(self, key, value, data):
        self.table.update(data, Query()[key] == value)

    def delete(self, key, value):
        self.table.remove(Query()[key] == value)
