#!/usr/bin/python3

import reservationapi
import configparser
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError)

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the hotel API
hotel  = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

# Your code goes here
print("Authentication", hotel._headers())

while True:
    try:
        slots = hotel.get_slots_available()
        print(slots)
    except:
        continue
    try:
        print("FOUND AVAILABLE SLOT:", slots[0].get('id'))
        msg = hotel.reserve_slot(slots[0].get('id'))
        print("RESERVED SLOT:", msg.get('id'))
        break
    except SlotUnavailableError:
        print("Slot", slots[0].get('id'), "was taken, not available anymore")
        print("Looking for another slot")

try:
    slots_held = hotel.get_slots_held()
    print("SLOTS HELD:", slots_held)
except:
    pass

while True:
    try:
        msg_release = hotel.release_slot(msg.get('id'))
        print(msg_release.get('message'))
        break
    except:
        print("DID NOT RELEASE SLOT, TRYING AGAIN")

try:
    slots_held = hotel.get_slots_held()
    print("SLOTS HELD:", slots_held)
except:
    pass
