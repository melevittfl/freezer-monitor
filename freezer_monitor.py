import os
import sys
import errno
import requests
from enum import Enum
import pickle
import logging
import datetime
import fcntl

from config import *

import sqlite3

STATE_FILE = 'data.pkl'


class State(Enum):
    def __str__(self):
        return str(self.name)

    ON = 1
    OFF = 2
    UNKNOWN = 3


def make_request(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as request_error:  # This is the correct syntax
        logging.error(request_error)
        return None
    return r


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
    resp = make_request('http://www.google.com')

    if resp is not None:
        if resp.status_code == requests.codes.ok:
            return True
        else:
            return False
    else:
        return False


def site_state():
    current_state = State.UNKNOWN
    if net_up():

        resp = make_request(SITE)

        if resp is not None:
            if resp.status_code == requests.codes.ok:
                logging.warning(resp.text)
                current_state = State.ON
            else:
                current_state = State.OFF
        else:
            current_state = State.OFF

    store_last_state(current_state)
    logging.info("site status is %s", current_state)
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

    logging.basicConfig(level=logging.WARN, filename='checksites.log',
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    last_state = load_last_state()

    current_state = site_state()

    if state_changed(last_state, current_state):
        logging.error("Power status changed. Is now %s", current_state)
        text_alert(current_state)

if __name__ == '__main__':
    f = open('.lock', 'w')
    try:
        fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    except IOError as e:
        if e.errno == errno.EAGAIN:
            sys.stderr.write("Another instance already running.")
            sys.exit(-1)

    main()






