import os
import sys
import errno
import requests
from enum import Enum
import pickle
import logging
import logging.config
import datetime
import fcntl
import socket
from config import *

import sqlite3
from sonos.sonosfind import found_kitchen_sonos


STATE_FILE = 'data.pkl'


class State(Enum):
    def __str__(self):
        return str(self.name)

    ON = 1
    OFF = 2
    UNKNOWN = 3


def load_last_state():
    last_state = State.UNKNOWN
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, 'rb') as picklefile:
            last_state = pickle.load(picklefile)

    return last_state


def store_last_state(state):
    with open(STATE_FILE, 'wb') as picklefile:
        pickle.dump(state, picklefile)


def net_up():
    """
    Test if the net is up by making a TCP connection to google's public DNS server
    :return: True if the connection succeeds, false otherwise
    """
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        logging.info("Network Up")
        return True
    except:
        return False


def site_state():
    current_state = State.UNKNOWN
    if net_up():

        if found_kitchen_sonos(KITCHEN_USN):
            current_state = State.ON
        else:
            logging.warning("Kitchen Sonos not found")
            current_state = State.OFF

    store_last_state(current_state)
    logging.info("Power status is %s", current_state)
    return current_state


def state_changed(last_state, current_state):
    if last_state is current_state:
        return False
    else:
        return True


def text_alert(current_state):
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    message = "{0} Power status has changed! Power is {1}".format(timestamp, current_state)
    params = {'api_key': NEXMO_API_KEY,
              'api_secret': NEXMO_API_SECRET,
              'to': MY_NUMBER,
              'from': NEXMO_NUMBER,
              'text': message
              }

    url = 'https://rest.nexmo.com/sms/json'

    response = requests.get(url, params=params)
    logging.warning(response.text)


def main():

    logging.config.dictConfig(LOG_SETTINGS)
    last_state = load_last_state()

    current_state = site_state()

    if state_changed(last_state, current_state):
        logging.error("Power status changed. Is now %s", current_state)
        text_alert(current_state)
    else:
        logging.info("Power status unchanged")

if __name__ == '__main__':
    f = open('.lock', 'w')
    try:
        fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    except IOError as e:
        if e.errno == errno.EAGAIN:
            sys.stderr.write("Another instance already running.")
            sys.exit(-1)

    main()
