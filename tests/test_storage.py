import unittest
import inspect
import json
from storage import Storage
from dataclasses import dataclass


@dataclass
class Message:
    value: str = None
    def tuples(self):
        o = json.loads(self.value.decode('ascii'))
        return tuple(o.values())


class TestStorage(unittest.TestCase):

    MESSAGE = {
        'site': 'storage-test',
        'elap': 500,
        'code': 200,
        'regx': 1,
        'unix': 1650880000
    }
    CONFIG = 'tests/test_config.conf'

    def setUp(self):
        self.storage = Storage(self.CONFIG)
        self.message = Message()
        self.message.value = json.dumps(self.MESSAGE).encode('ascii')

    def test_create_tables(self):
        connection = self.storage.connection
        c = connection.cursor()
        c.execute('DROP TABLE IF EXISTS data;')
        c.execute('DROP TABLE IF EXISTS sites;')
        connection.commit()
        c.close()
        self.storage.initialize_database()

    def test_send_data(self):
        self.storage.send(self.message)

    def test_validate_data(self):
        connection = self.storage.connection
        c = connection.cursor()
        c.execute('SELECT * FROM data;')
        data = c.fetchall()
        self.assertEqual(len(data), 1)
        c.execute('SELECT * FROM sites;')
        sites = c.fetchall()
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0][1], self.MESSAGE['site'])
        self.assertEqual(
            data[0], 
            (1, sites[0][0],) + self.message.tuples()[1:]
        )
        c.close()


if __name__ == "__main__":
    test_src = inspect.getsource(TestStorage)
    unittest.TestLoader.sortTestMethodsUsing = lambda _, x, y: (
        test_src.index(f"def {x}") - test_src.index(f"def {y}")
    )
    unittest.main()
