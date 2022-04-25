import logging
import requests
import re
import json
from time import sleep, time
from kafka import KafkaProducer
from threading import Thread
from configparser import ConfigParser


logging.basicConfig(
    format="%(asctime)s: %(message)s", 
    level="INFO", 
    datefmt="%H:%M:%S"
)


class Observer(Thread):

    REGEXP_MATCH = 1
    REGEXP_NO_MATCH = 2
    REGEXP_MATCH_AND_CHANGE = 3

    def __init__(self, id, site, regexp, config):
        """ Observer can check metrics from one website
        :param id: Thread specific id
        :param site: Checked website
        :param regexp: Regex pattern searched on a website(s)
        :param config: Config dict
        :return:
        """
        Thread.__init__(self)
        self.config = config
        self.id = id
        self.site = site
        self.regexp = regexp
        self.producer = KafkaProducer(
            bootstrap_servers=config['KAFKA']['bootstrap_server'],
            security_protocol=config['KAFKA']['security_protocol'],
            ssl_cafile=config['KAFKA']['ssl_cafile'],
            ssl_certfile=config['KAFKA']['ssl_certfile'],
            ssl_keyfile=config['KAFKA']['ssl_keyfile']
        )

    def run(self):
        """ Site checker
        :return:
        """
        pre_r_code = None
        pre_r_regx = None
        while True:
            message = {
                'site': self.site,
                'code': None,
                'regx': None
            }
            r = requests.get(self.site, timeout=5)
            if r.status_code != pre_r_code:
                pre_r_code = r.status_code
                message['code'] = pre_r_code
            if self.regexp is not None:
                cur_r_regx = re.findall(self.regexp, r.text)
                if pre_r_regx != cur_r_regx:
                    if pre_r_regx is None:
                        if cur_r_regx:
                            message['regx'] = self.REGEXP_MATCH
                        else:
                            message['regx'] = self.REGEXP_NO_MATCH
                    elif pre_r_regx and not cur_r_regx:
                        message['regx'] = self.REGEXP_NO_MATCH
                    elif not pre_r_regx and cur_r_regx:
                        message['regx'] = self.REGEXP_MATCH
                    else:
                        message['regx'] = self.REGEXP_MATCH_AND_CHANGE
                    pre_r_regx = cur_r_regx
            message['elap'] = int(r.elapsed.microseconds / 1000)
            message['unix'] = int(time())
            self.producer.send(
                self.config['KAFKA']['topic'],
                json.dumps(message).encode('ascii')
            )
            if len(self.config['GENERAL']['interval']): 
                sleep(int(self.config['GENERAL']['interval']))
            else: 
                break


class Monitor:

    def __init__(self, sites:list, regexp:str=None, config_path:str='config.conf'):
        """ Monitor creates needed amount of observers for website metrics
        :param sites: List of websites to be monitored
        :param regexp: Regex pattern searched on a website(s)
        :param config_path: Path to config file
        :return:
        """
        self.config = ConfigParser()
        self.config.read(config_path)
        self.sites = sites
        self.regexp = regexp
        self.threads = list()

    def start_monitoring(self):
        """ Method will create new thread for each observed website
        :return:
        """
        for i in range(len(self.sites)):
            logging.info('Creating monitoring for site: %s', self.sites[i])
            observer = Observer(i, self.sites[i], self.regexp, self.config)
            self.threads.append(observer)
            observer.start()

    def start(self):
        """ Start monitoring and give basic information about used parameters
        :return:
        """
        logging.info('Starting monitoring for sites: {}{}'.format(
            ', '.join(self.sites),
            ' with the regexp: {}'.format(
                self.regexp if self.regexp is not None else '')
            )
        )
        self.start_monitoring()
