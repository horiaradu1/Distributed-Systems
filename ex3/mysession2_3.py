#!/usr/bin/python3

import sys
from sys import call_tracing
import time
import reservationapi
import configparser
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError, ReservationLimitError)

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the hotel API
hotel  = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))
                                       
band  = reservationapi.ReservationApi(config['band']['url'],
                                       config['band']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

def check_release_slots_held(booking, name: str = ''):
    """
        Function to check and release held bookings
    """
    print("CHECKING ALREADY HELD %s SLOTS..." % (name))
    slots_held = booking.get_slots_held()
    if len(slots_held) > 0:
        while len(slots_held) > 0:
            print("RELEASING ALREADY HELD %s SLOTS..." % (name))
            for key in slots_held:
                print("RELEASING SLOT:", key.get('id'))
                print(booking.release_slot(key.get('id')))
            slots_held = booking.get_slots_held()
        print("ALL HELD %s SLOTS RELEASED %s" % (name, slots_held))
    else:
        print("NO %s SLOTS %s" % (name, slots_held))
    return slots_held

def check_available_slots(booking_1, booking_2, name_1: str = '', name_2: str = ''):
    """
        Function to check available slots of 2 bookings
    """
    slots_1 = dict()
    slots_2 = dict()
    while True:
        try:
            print("LOOKING UP ALL AVAILABLE "+name_1+" SLOTS...")
            slots_1 = booking_1.get_slots_available()
            print("GOT AVAILABLE "+name_1+" SLOTS")
            print("LOOKING UP ALL AVAILABLE "+name_2+" SLOTS...")
            slots_2 = booking_2.get_slots_available()
            print("GOT AVAILABLE "+name_2+" SLOTS")
            break
        except Exception as e:
            print("!!ERROR!!")
            print(e)
        
    return slots_1, slots_2

def earliest_common(dict_1: dict, dict_2: dict):
    """
        Function to look for the earliest common slot of two dictionaries
    """
    list_1 = []
    list_2 = []

    for key in dict_1:
        list_1.append(key.get('id'))
    for key in dict_2:
        list_2.append(key.get('id'))

    # print(list_1)
    # print(list_2)

    for i in list_1:
        if i in list_2:
            earliest = i
            return earliest

    return None

def booking(booking_1, booking_2, name_1, name_2, current_best_slot):
    """
        Function to look for a common booking
        and decide if to take it or not
        if it is better that what you currently have
    """
    # check availability of common slots
    slots_1, slots_2 = check_available_slots(booking_1, booking_2, name_1, name_2)
    available_slots = earliest_common(slots_1, slots_2)

    if available_slots == None:
        print("NO SLOT FOUND FOR BOTH BOOKINGS")
        return None
    print("EARLIEST COMMON SLOT FOR NOW:", available_slots)
    if int(current_best_slot) <= int(available_slots):
        print("SLOT FOUND IS NOT BETTER THAN CURRENT BEST")
        return None

    print("RESERVING THAT SLOT FOR BOTH BOOKINGS...")

    # book earliest common slot
    try:
        print(booking_1.reserve_slot(str(available_slots)))
    except SlotUnavailableError:
        print("SLOT RESERVED MEANWHILE, TRYING NEXT")
        reserved_slot = booking(booking_1, booking_2, name_1, name_2, current_best_slot)
        return reserved_slot

    try:
        print(booking_2.reserve_slot(str(available_slots)))
        reserved_slot = available_slots
    except SlotUnavailableError:
        print("SLOT RESERVED MEANWHILE, TRYING NEXT, ALSO RELEASING PREVIOUS RESERVED BOOKING "+name_1+" SLOT")
        print(booking_1.release_slot(str(available_slots)))
        reserved_slot = booking(booking_1, booking_2, name_1, name_2, current_best_slot)
        return reserved_slot
    
    return reserved_slot

# one second delay in each request in reservationapi.py

# variable declarations
current_best = '10000'
reserved_one = False
booking_number = 1

# !! CHANGE HERE THE NUMBER OF TIMES YOU WANT TO LOOK FOR A SLOT AFTER SORTING OUT CURRENT BOOKINGS
recheck_booking_number = 3

# recheck at least once for better bookings
while True:
    # sort out current bookings
    try:
        print("SORTING OUT CURRENT BOOKINGS")
        slots_held_hotel = hotel.get_slots_held()
        slots_held_band = band.get_slots_held()
        #print(slots_held_hotel, slots_held_hotel)
        # if any on the cases, act and sort acordingly
        if len(slots_held_hotel) == 2 and len(slots_held_band) == 2 and slots_held_hotel[0].get('id') == slots_held_band[0].get('id') and slots_held_hotel[1].get('id') == slots_held_band[1].get('id'):
            print("ALREADY 2 HELD SLOTS, REMOVING THE LATER ONE")
            if int(slots_held_hotel[0].get('id')) > int(slots_held_hotel[1].get('id')):
                slot_to_remove = slots_held_hotel[0].get('id')
                current_best = slots_held_hotel[1].get('id')
            else:
                slot_to_remove = slots_held_hotel[1].get('id')
                current_best = slots_held_hotel[0].get('id')
            hotel.release_slot(str(slot_to_remove))
            band.release_slot(str(slot_to_remove))
            reserved_one = True
        elif len(slots_held_hotel) == 1 and len(slots_held_band) == 1 and slots_held_hotel[0].get('id') == slots_held_band[0].get('id'):
            print("YOU CURRENTLY HAVE 1 SLOT IN HOTEL MATCHING 1 IN BAND")
            current_best = slots_held_hotel[0].get('id')
            reserved_one = True
        elif len(slots_held_hotel) == 0 and len(slots_held_band) == 0:
            print("NO SLOTS RESERVED")
            reserved_slot_first = booking(hotel, band, "hotel", "band", current_best)
            if reserved_slot_first != None:
                current_best = reserved_slot_first
                print("RESERVED SLOT FIRST TIME:", reserved_slot_first)
                reserved_one = True
        else:
            # otherwise, if there was a problem, release all bookings and get a new one
            print("RELEASING ALL BOOKINGS AND GETTING A NEW ONE")
            check_release_slots_held(hotel, "hotel")
            check_release_slots_held(band, "band")
            reserved_slot_first = booking(hotel, band, "hotel", "band", current_best)
            if reserved_slot_first != None:
                current_best = reserved_slot_first
                print("RESERVED SLOT FIRST TIME:", reserved_slot_first)
                reserved_one = True
        slots_held_hotel = hotel.get_slots_held()
        slots_held_band = band.get_slots_held()
        print("CURRENTLY HELD SLOTS: hotel - %s | band - %s" % (slots_held_hotel, slots_held_band))
    except (BadRequestError, InvalidTokenError) as ex:
        print("!!ERROR!!")
        print(ex)
        print("EXITING...")
        exit()
    except Exception as e:
        print("!!ERROR!!")
        print(e)
        print("TRYING TO RUN SESSION AGAIN")
        continue

    while recheck_booking_number >= booking_number:
        # check for a better booking recheck_booking_number number of times
        print("\nCHECK-BOOKING", booking_number,"NUMBER OF TIMES")
        try:
            # check availability of common slots
            reserved_slot = booking(hotel, band, "hotel", "band", current_best)

            # if no better slot found, skip
            if reserved_slot == None:
                booking_number += 1
                continue

            print("RESERVED SLOT:", reserved_slot)

            # if reserved another slot, remove the later one
            slots_held_hotel = hotel.get_slots_held()
            slots_held_band = band.get_slots_held()
            if len(slots_held_hotel) == 2 and len(slots_held_band) == 2:
                print("REMOVING THE LATER SLOT")
                if int(slots_held_hotel[0].get('id')) > int(slots_held_hotel[1].get('id')):
                    slot_to_remove = slots_held_hotel[0].get('id')
                    current_best = slots_held_hotel[1].get('id')
                else:
                    slot_to_remove = slots_held_hotel[1].get('id')
                    current_best = slots_held_hotel[0].get('id')
                hotel.release_slot(str(slot_to_remove))
                band.release_slot(str(slot_to_remove))
                reserved_one = True

            # show what is currently reserved
            slots_held_hotel = hotel.get_slots_held()
            slots_held_band = band.get_slots_held()
            print("RESERVED NOW", slots_held_hotel, slots_held_band)
            reserved_one = True
            booking_number += 1
        except (BadRequestError, InvalidTokenError) as ex:
            print("!!ERROR!!")
            print(ex)
            print("EXITING...")
            exit()
        except ReservationLimitError as ex:
            print("!!ERROR!!")
            print(e)
            reserved_one = False
            booking_number -= 1
            break
        except Exception as e:
            print("!!ERROR!!")
            print(e)
            print("TRYING TO RUN SESSION AGAIN")
            booking_number -= 1
            continue

    if reserved_one == True:
        break

# show what is reserved at the end
slots_held_hotel = hotel.get_slots_held()
slots_held_band = band.get_slots_held()
print("FINALLY HELD SLOTS:\n", slots_held_hotel,slots_held_band)