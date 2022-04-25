from monitor import Monitor


monitor = Monitor(
    ['https://www.unixtimestamp.com/',
    'https://aiven.io/'],
    '/5[0-9]|60/gm',
    'config.conf'
)
monitor.start()
