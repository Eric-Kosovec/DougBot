import pickle


class KVStore:

    _KEY_COLUMN = 'kv_key'
    _VALUE_COLUMN = 'kv_value'
    _TABLE_SCHEMA = f'{_KEY_COLUMN} TEXT PRIMARY KEY, {_VALUE_COLUMN} BLOB'

    # TODO PROTECT FROM SQL-INJECTION. SQLITE PYTHON DOESN'T ALLOW PARAMETERIZING TABLE NAMES AND COLUMN NAMES
    # TODO CACHING

    def __init__(self, db, table_name):
        if db is None or table_name is None:
            raise ValueError('KVStore init given None value')
        if table_name.startswith('_'):
            raise ValueError('KVStore table name cannot start with an underscore')

        self._db = db
        self._table = table_name
        self._iterator = None

        if not self._db.has_table(self._table):
            self._db.execute(f'CREATE TABLE IF NOT EXISTS {self._table}({self._TABLE_SCHEMA})')

    def insert(self, key, value):
        if key is None or value is None:
            raise ValueError('KVStore insert given None value')
        if type(key) != str:
            raise ValueError('KVStore insert key must be a string')

        self._db.execute(f'REPLACE INTO {self._table} VALUES (?, ?)', (key, self._serialize_value(value),))

    def remove(self, key):
        if key is None:
            raise ValueError('KVStore remove given None value')
        if type(key) != str:
            raise ValueError('KVStore remove key must be a string')

        self._db.execute(f'DELETE FROM {self._table} WHERE {self._KEY_COLUMN} = ?', (key,))

    def contains(self, key, value=None):
        if key is None:
            raise ValueError('KVStore contains given None value')
        if type(key) != str:
            raise ValueError('KVStore contains key must be a string')

        if value is None:
            result = self._db.execute(f'SELECT {self._KEY_COLUMN} FROM {self._table}')
        else:
            serialized_value = self._serialize_value(value)
            result = self._db.execute(f'SELECT {self._KEY_COLUMN} FROM {self._table} WHERE {self._KEY_COLUMN} = ? and {self._VALUE_COLUMN} = ?', (key, serialized_value,))
        try:
            return result is not None and next(result) is not None
        except StopIteration:
            return False

    def get(self, key):
        if key is None:
            raise ValueError('KVStore get given None value')
        if type(key) != str:
            raise ValueError('KVStore get key must be a string')

        result = self._db.execute(f'SELECT {self._VALUE_COLUMN} FROM {self._table} WHERE {self._KEY_COLUMN} = ?', (key,))
        if result is None:
            return None
        try:
            return self._deserialize_value(next(result)[0])
        except StopIteration:
            return None

    @staticmethod
    def _serialize_value(value):
        if value is None:
            return b'\0'
        return pickle.dumps(value)

    @staticmethod
    def _deserialize_value(serial):
        if serial is None:
            return None
        return pickle.loads(serial)

    def __getitem__(self, key):
        if key is None:
            return None
        return self.get(key)

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __iter__(self):
        self._iterator = self._db.execute(f'SELECT {self._KEY_COLUMN}, {self._VALUE_COLUMN} FROM {self._table}')
        return self

    def __next__(self):
        if self._iterator is None:
            raise StopIteration
        try:
            item = next(self._iterator)
            return item[0], self._deserialize_value(item[1])
        except StopIteration:
            self._iterator = None
            raise StopIteration
