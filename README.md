# Website availability monitor

[![Python application](https://github.com/jjaapro/websiteavailabilitymonitor/actions/workflows/validation.yml/badge.svg)](https://github.com/jjaapro/websiteavailabilitymonitor/actions/workflows/validation.yml)

## Overview

This project was created to test Kafka. Solution monitors website availability over the network, produces metrics about this and passes these events through an cloud Kafka instance into an cloud PostgreSQL database.

Solution contains two packages, monitor and storage. Monitor can observe any amount of websites and storage will store all metrics gathered by monitoring. These two packages are not dependend of each other, so both packages can be used separately.

Metrics gathered are HTTP response time, status code and match for regex pattern. Regex pattern match can have three different state.

States | |
--- | ---  
Match | 1
No Match | 2
Changed | 3

Although HTTP response time is stored to database everytime when check is completed, status code and regex pattern matching are event based information.

## Getting Started

Install packages, either with the command install or pip_install. Command pip_install is custom command which will install packages using subprocess.

```bash
python setup.py install
```

or

```bash
python setup.py pip_install
```

Check configuration from config.conf and change at least fields marked with \<change me\> when using locally installed Kafka and PostgreSQL. General setting interval will control website check cycle.

Simple example using both packages, monitor and storage. Response time, returned status code and regex pattern will be checked from website(s) at interval given in configuration. Monitor observers two webpages and tries to find numbers between 50 and 60 according to given regex pattern.

```bash
from storage import Storage


storage = Storage('config.conf')
storage.start()
```

and

```bash
from monitor import Monitor


monitor = Monitor(
    ['https://www.unixtimestamp.com/',
    'https://github.com/jjaapro/'],
    '/5[0-9]|60/gm',
    'config.conf'
)
monitor.start()
```

Start each of these examples in separate console. Both examples can be found from /examples. Examples can be started with the commands

```bash
python examples/consumer.py
```

and

```bash
python examples/producer.py
```
