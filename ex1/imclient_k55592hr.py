import im
from os import system
import time
import threading
import sys
from datetime import datetime

server = im.IMServerProxy('https://web.cs.manchester.ac.uk/k55592hr/comp28112_ex1/IMserver.php')
global sent
global userSender
global once

# Function to reset the page
def resetPage():
    system('clear')
    print("CURRENTLY CONNECTED AS: {}".format(userSender))

# Function to display all users
def showUsers():
    for i in server.keys():
        print(i.decode('utf-8'))

# Function to refresh the page and wait
def waitForMes():
    resetPage()
    print("Waiting for message...")

# Initiation function for __waiting__
def waiting_init():
    server.__setitem__("__waiting__", '')

# Function to declare the username
def userSender_init():
    system('clear')
    print("Hello!")
    userSender = input("To send a message, please enter your username: ")
    # Used for debugging; clearing the server
    # if userSender == "clear":
    #     server.clear()
    #     exit()
    server.__setitem__(userSender, '')
    return userSender

# The thread function that selects all the states the client can be in
def checking():
    global sent
    global userSender
    global once
    while True:
        time.sleep(3)
        # If locally you have sent a message
        if sent == True:
            # Wait for the message, while the one in the waiting variable key is the local user
            if server.__getitem__("__waiting__").decode('utf-8') == str(userSender + "\n"):
                waitForMes()
            # And when the other person sends a message, go back to sending
            else:
                resetPage()
                if server.__getitem__("__waiting__").decode('utf-8') == "\n":
                    print("{} - ".format(userSender), end = '')
                    sys.stdout.flush()
                sent = False
                once = True
        # Waiting for user to send a message
        if sent == False:
            if once == True:
                if server.__getitem__("__waiting__").decode('utf-8') != str(userSender + "\n") and server.__getitem__("__waiting__").decode('utf-8') != "\n":
                    if server[server.__getitem__("__waiting__").decode('utf-8').rstrip()].decode('utf-8').rstrip() != "":
                        resetPage()
                        print("{} - {}".format(server.__getitem__("__waiting__").decode('utf-8').rstrip(), server.__getitem__(server.__getitem__("__waiting__").decode('utf-8').rstrip()).decode('utf-8')))
                        print("{} - ".format(userSender), end = '')
                        sys.stdout.flush()
                    once = False

# Variables declaration and initializations
userSender = userSender_init()
resetPage()
waiting_init()
sent = False
once = True
checker = threading.Thread(target=checking)
checker.daemon = True
checker.start()


print("{} - ".format(userSender), end = '')
# Loop to keep the messaging client and thread in
while True:
    if sent is False:
        message = input()
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # messageSent = str(message + " [" + current_time + "]")
        server.__setitem__(userSender, message)
        server.__setitem__("__waiting__", userSender)
        sent = True
