import inspect


class KVStore:

    _KV_STORE_TABLE_SCHEMA = 'key TEXT PRIMARY KEY, value BLOB'

    def __init__(self, base_db):
        self._base_db = base_db

    def insert(self, table, key, value):
        if table is None or key is None or value is None:
            raise ValueError('KVStore insert given None value')
        if type(key) != str:
            raise ValueError('KVStore key must be a string')
        if table.startswith('_'):
            raise ValueError('KVStore table name cannot start with an underscore')
        if not self._base_db.has_table(table):
            self._base_db.create_table(table, KVStore._KV_STORE_TABLE_SCHEMA)
        self._base_db.insert_into(table, (key, self._serialize_value(value),))

    def remove(self, table, key, value=None):
        if table is None or key is None:
            raise ValueError('KVStore remove given None value')
        if type(key) != str:
            raise ValueError('KVStore key must be a string')
        if table.startswith('_'):
            raise ValueError('KVStore table name cannot start with an underscore')
        if value is None:
            self._base_db.delete_from(table, f'key = {key}')
        else:
            self._base_db.delete_from(table, f'key = {key} and value = {self._serialize_value(value)}')

    def contains(self, table, key, value=None):
        if table is None or key is None:
            raise ValueError('KVStore contains given None value')
        if type(key) != str:
            raise ValueError('KVStore key must be a string')
        if table.startswith('_'):
            raise ValueError('KVStore table name cannot start with an underscore')
        self._base_db.has_row('key, value', table, f'key = {key} and value = {self._serialize_value(value)}')

    def get(self, table, key):
        if table is None or key is None:
            raise ValueError('KVStore get given None value')
        for row in self._base_db.select_from('value', table, f'key = {key}'):
            yield row

    def close(self):
        self._base_db.close()

    @staticmethod
    def _serialize_value(value):
        if value is None:
            return 'NULL'
        # TODO ACTUALLY SERIALIZE
        return value

    # ? = kv[table_name][key] and
    # kv[table_name][key] = ?
    def __getitem__(self, table):
        class TableGetValue:
            def __init__(self, parent):
                self.parent = parent

            def __getitem__(self, key):
                return self.parent.get(table, key)

            def __setitem__(self, key, value):
                if key is None:
                    return
                print('SET ITEM')
                self.parent.insert(table, key, value)
        return TableGetValue(self)

    # for k, v in kv
    def __iter__(self):
        pass


'''
    @staticmethod
    def _get_caller_package():
        caller_frame = inspect.stack()[2]
        module = inspect.getmodule(caller_frame[0])
        module_name = module.__name__ if '.' not in module.__name__ else module.__name__[:module.__name__.rfind('.')]
        return module_name.replace('.', '_')
'''
