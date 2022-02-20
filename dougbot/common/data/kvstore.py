import pickle


class KVStore:

    _KEY_COLUMN = 'kv_key'
    _VALUE_COLUMN = 'kv_value'
    _TABLE_SCHEMA = f'{_KEY_COLUMN} TEXT PRIMARY KEY, {_VALUE_COLUMN} BLOB'

    ''' Not to be created directly. Get from bot class. '''
    def __init__(self, db, table_name):
        if table_name.startswith('_'):
            raise ValueError(f"KVStore table name '{table_name}' cannot start with an underscore")
        if not table_name.isidentifier():
            raise ValueError(f"KVStore table name '{table_name}' is invalid")

        self._db = db
        self._table_name = table_name
        self._iterator = None

        self._db.execute(f'CREATE TABLE IF NOT EXISTS {self._table_name}({self._TABLE_SCHEMA})')

    def insert(self, key, value):
        if type(key) != str:
            raise ValueError('KVStore insert key must be a string')

        self._db.execute(f'REPLACE INTO {self._table_name} VALUES (?, ?)', (key, self._serialize_value(value),))

    async def insert_async(self, key, value):
        self.insert(key, value)

    def remove(self, key):
        if type(key) != str:
            raise ValueError('KVStore remove key must be a string')

        self._db.execute(f'DELETE FROM {self._table_name} WHERE {self._KEY_COLUMN} = ?', (key,))

    async def remove_async(self, key):
        self.remove(key)

    def contains(self, key, value=None):
        if type(key) != str:
            raise ValueError('KVStore contains key must be a string')

        if value is None:
            result = self._db.execute(f'SELECT {self._KEY_COLUMN} FROM {self._table_name}')
        else:
            serialized_value = self._serialize_value(value)
            result = self._db.execute(f'SELECT {self._KEY_COLUMN} FROM {self._table_name} WHERE {self._KEY_COLUMN} = ? and {self._VALUE_COLUMN} = ?', (key, serialized_value,))

        try:
            return result is not None and next(result) is not None
        except StopIteration:
            return False

    async def contains_async(self, key, value=None):
        return self.contains(key, value)

    def get(self, key):
        if type(key) != str:
            raise ValueError('KVStore get key must be a string')

        result = self._db.execute(f'SELECT {self._VALUE_COLUMN} FROM {self._table_name} WHERE {self._KEY_COLUMN} = ?', (key,))

        try:
            return self._deserialize_value(next(result)[0])
        except StopIteration or TypeError:
            raise ValueError('KVStore get key does not exist')

    async def get_async(self, key):
        return self.get(key)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        self.remove(key)

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __iter__(self):
        self._iterator = self._db.execute(f'SELECT {self._KEY_COLUMN}, {self._VALUE_COLUMN} FROM {self._table_name}')
        return self

    def __next__(self):
        try:
            item = next(self._iterator)
            return item[0], self._deserialize_value(item[1])
        except StopIteration or TypeError:
            self._iterator = None
            raise

    @staticmethod
    def _serialize_value(value):
        return b'\0' if value is None else pickle.dumps(value)

    @staticmethod
    def _deserialize_value(serial):
        return None if serial is None else pickle.loads(serial)
