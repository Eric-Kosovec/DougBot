import pickle


class KVStore:

    _KV_STORE_KEY_COLUMN = 'kv_key'
    _KV_STORE_VALUE_COLUMN = 'kv_value'
    _KV_STORE_TABLE_SCHEMA = f'{_KV_STORE_KEY_COLUMN} TEXT PRIMARY KEY, {_KV_STORE_VALUE_COLUMN} BLOB'

    # TODO PROTECT FROM SQL-INJECTION. SQLITE PYTHON DOESN'T ALLOW PARAMETERIZING TABLE NAMES AND COLUMN NAMES

    def __init__(self, db, table):
        if db is None or table is None:
            raise ValueError('KVStore init given None value')
        if table.startswith('_'):
            raise ValueError('KVStore table name cannot start with an underscore')

        self._db = db
        self._table = table
        if not self._db.has_table(self._table):
            print('HAS NO TABLE')
            try:
                print('EXECUTE')
                self._db.execute(f'CREATE TABLE IF NOT EXISTS {self._table}({self._KV_STORE_TABLE_SCHEMA})')
                print('AFTER EXECUTE')
            except Exception as e:
                print(f'ERROR: {e}')
        print('HAS TABLE')

    def insert(self, key, value):
        if key is None or value is None:
            raise ValueError('KVStore insert given None value')
        if type(key) != str:
            raise ValueError('KVStore insert key must be a string')
        print('INSERT')
        self._db.execute(f'REPLACE INTO {self._table} VALUES (?, ?)', (key, self._serialize_value(value),))

    def remove(self, key, value=None):
        if key is None:
            raise ValueError('KVStore remove given None value')
        if type(key) != str:
            raise ValueError('KVStore remove key must be a string')

        if value is None:
            self._db.execute(f'DELETE FROM {self._table} WHERE {self._KV_STORE_KEY_COLUMN} = ?', (key,))
        else:
            self._db.execute(f'DELETE FROM {self._table} WHERE {self._KV_STORE_KEY_COLUMN} = ? AND '
                             f'{self._KV_STORE_VALUE_COLUMN} = ?', (key, value,))

    def contains(self, key, value=None):
        if key is None:
            raise ValueError('KVStore contains given None value')
        if type(key) != str:
            raise ValueError('KVStore contains key must be a string')

        if value is None:
            result = self._db.execute(f'SELECT {self._KV_STORE_KEY_COLUMN} FROM {self._table}')
        else:
            result = self._db.execute(f'SELECT {self._KV_STORE_KEY_COLUMN} FROM {self._table} WHERE '
                                      f'{self._KV_STORE_KEY_COLUMN} = ? and {self._KV_STORE_VALUE_COLUMN} = ?',
                                      (key, value,))
        return result is not None and next(result) is not None

    def get(self, key):
        if key is None:
            raise ValueError('KVStore get given None value')
        if type(key) != str:
            raise ValueError('KVStore get key must be a string')

        try:
            result = self._db.execute(f'SELECT {self._KV_STORE_VALUE_COLUMN} FROM {self._table} WHERE '
                                      f'{self._KV_STORE_KEY_COLUMN} = ?', (key,))
            if result is None:
                return None
            return self._deserialize_value(next(result))
        except Exception as e:
            print(e)

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

    # for k, v in kv
    def __iter__(self):
        # TODO
        pass
