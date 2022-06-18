import time
import random
from os import path
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
import requests
import socket
import httpx
from random import choice
import yaml
from datetime import datetime

URL = "https://canyouseeme.org/"

def get_host_and_ports():
    global HOST, PORTS, user_agent_list
    with open('user_agents.list') as f:
        user_agent_list = f.read().splitlines()

def parse_scan_data():
    global HOST, PORTS
    if socket.gethostbyname(HOST) != HOST:
        HOST = socket.gethostbyname(HOST)
        global spoofed_payload
        spoofed_payload = {"ports": str(PORTS), "HOST": HOST}

def scan_ports():
    global HOST, PORTS, spoofed_payload, PORTS_STATE
    timestampStr = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    print('\n## Scanning action at:', timestampStr, '###')
    print("Starting port scan against: " + HOST + "\n")
    for port in PORTS:
        user_agent = choice(user_agent_list)

        spoofed_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': URL[8:-1],
            'Origin': URL[:-1],
            'X-Forwarded-For': HOST,
            'Client-Ip': HOST,
            'Via': HOST,
            'Referer': URL,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-agent': user_agent
        }

        spoofed_payload = {"port": str(port), "HOST": HOST}

        r = httpx.post(URL, headers=spoofed_headers,
                       data=spoofed_payload, timeout=None)

        if "Success:" in str(r.content):
            print("Port " + str(port) + " opened.")
            PORTS_STATE[port] = 1
        else:
             print("Port " + str(port) + " closed.")
             PORTS_STATE[port] = 0


class OpenPortsCollector(object):
    global PORTS_STATE
    def __init__(self):
        pass
    def collect(self):
        # print('refreshing prometheus')

        gauge = GaugeMetricFamily("python_is_port_open", "fuck off", labels=["portNumber"])
        for port, state in PORTS_STATE.items():
            # print("going to register port "+ str(port) + " with value "+ str(state))
            gauge.add_metric([str(port)], str(state))
        yield gauge


def get_config(skip):
    global service_port, frequency, HOST, PORTS
    if (skip): return
    print('Reading config from config.yml.....', )
    configFile = 'config/config.yml'
    if path.exists(configFile):
        with open(configFile, 'r') as config_file:
            try:
                config = yaml.safe_load(config_file)

                service_port = config['service_port']
                print('setted service_port = '+str(service_port))

                frequency = config['scrape_frequency']
                print('setted frequency = '+str(frequency))

                HOST = config['host_to_check']
                print('setted host_to_check = '+str(HOST))

                PORTS = config['ports_tocheck']
                print('setted ports_tocheck = '+str(PORTS))

                config_file.close()

            except yaml.YAMLError as error:
                print(error)


def doStuff(skipConfig):
    print('ok! let''s work! it''s ', datetime.now().strftime("%d-%b-%Y %H:%M:%S"))
    get_config(skipConfig)
    get_host_and_ports()
    parse_scan_data()
    scan_ports()


if __name__ == "__main__":
    global PORTS_STATE, frequency, service_port
    print('Hi! Welcome to port checker python script. ### Kudos to canyouseeme.org, J0hn8uff3r, matthewzhaocc.com and xeviff ;-) ###')
    skipConfig = False
    get_config(skipConfig)
    skipConfig = True
    start_http_server(service_port)
    PORTS_STATE = {}
    REGISTRY.register(OpenPortsCollector())

    while True:
        doStuff(skipConfig)
        skipConfig = False
        print('\nNot scanning ports again until', frequency, 'seconds later')
        time.sleep(frequency)
