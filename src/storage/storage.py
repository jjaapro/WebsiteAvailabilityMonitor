import logging
import json
import psycopg2
from kafka import KafkaConsumer
from threading import Thread
from configparser import ConfigParser


logging.basicConfig(
    format="%(asctime)s: %(message)s",
    level="INFO",
    datefmt="%H:%M:%S"
)


class Listener(Thread):

    def __init__(self, listener, config_path:str='config.conf'):
        """ Listener for kafka consumer
        :param listener: Any function that can handle message as an parameter
        :param config_path: Path to config file
        :return:
        """
        Thread.__init__(self)
        self.config = ConfigParser()
        self.config.read(config_path)
        self.listener = listener
        self.consumer = KafkaConsumer(
            self.config['KAFKA']['topic'],
            bootstrap_servers=self.config['KAFKA']['bootstrap_server'],
            client_id=self.config['KAFKA']['client_id'],
            group_id=self.config['KAFKA']['group_id'],
            security_protocol=self.config['KAFKA']['security_protocol'],
            ssl_cafile=self.config['KAFKA']['ssl_cafile'],
            ssl_certfile=self.config['KAFKA']['ssl_certfile'],
            ssl_keyfile=self.config['KAFKA']['ssl_keyfile']
        )

    def run(self):
        """ Kafka consumer polling
        :return:
        """
        self.consumer.poll(int(self.config['GENERAL']['interval']))
        for i in self.consumer: 
            self.listener(i)


class Storage:

    def __init__(self, config_path:str='config.conf'): 
        """ Storage for consumed data
        :param config_path: Path to config file
        :return:
        """
        self.config = ConfigParser()
        self.config.read(config_path)
        self.connection = psycopg2.connect(
            database=self.config['POSTGRESQL']['database'],
            user=self.config['POSTGRESQL']['user'],
            password=self.config['POSTGRESQL']['password'],
            host=self.config['POSTGRESQL']['host'],
            port=self.config['POSTGRESQL']['port']
        )

    def initialize_database(self):
        """ Create database tables if not exist
        :return:
        """
        c = self.connection.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sites(
            site_id int GENERATED ALWAYS AS IDENTITY, 
            site text UNIQUE NOT NULL, 
            PRIMARY KEY(site_id))""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS data(
            data_id int GENERATED ALWAYS AS IDENTITY, 
            site_id int, 
            response_time int,
            response_code int, 
            match_type smallint, 
            unix_time int NOT NULL, 
            PRIMARY KEY(data_id), 
            FOREIGN KEY(site_id) REFERENCES sites(site_id) ON DELETE CASCADE)""")
        self.connection.commit()
        c.close()

    @staticmethod
    def register(listener):
        """ Register listener for kafka consumer
        :param listener: Any function that can handle message as an parameter
        :return:
        """
        thread = Listener(listener)
        thread.start()
        thread.join()

    def send(self, message):
        """ Insert data to the postgresql database
        :param message: Encoded dict message containing keys: 
                        site, elap, code,regx and unix.
        :return:
        """
        logging.info('Message: {}'.format(message.value))
        o = json.loads(message.value.decode('ascii'))
        c = self.connection.cursor()
        c.execute("""
            INSERT INTO sites(site) 
            VALUES (%s)
            ON CONFLICT DO NOTHING""", (o['site'],)
        )
        c.execute("""
            INSERT INTO data(
                site_id, 
                response_time, 
                response_code, 
                match_type, 
                unix_time) 
            VALUES (
                (SELECT site_id FROM sites WHERE site = %s),
                %s,%s,%s,%s)""", (
            o['site'],
            o['elap'],
            o['code'],
            o['regx'],
            o['unix'])
        )
        self.connection.commit()
        c.close()

    def start(self):
        """ Initialize database and register listener for kafka consumer 
        :return:
        """
        self.initialize_database()
        self.register(self.send)
