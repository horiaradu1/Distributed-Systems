"""

IRC client exemplar.

"""

import sys
from ex2utils import Client

import time


class IRCClient(Client):

    def onMessage(self, socket, message):
    	# *** process incoming messages here ***
        (command, _, parameter) = message.strip().partition(' ')
        
        if command == "MESSAGE":
            (sender, _, msg) = parameter.strip().partition(' ')
            print("ALL MESSAGE FROM " + sender + " > " + msg + "\n")
        elif command == "PRIVATE":
            (sender, _, recieverMessage) = parameter.strip().partition(' ')
            (_, _, msg) = recieverMessage.strip().partition(' ')
            print("PRIVATE MSG FROM " + sender + " > " + msg + "\n")
        elif command == "REGISTER":
            print("User joined: " + parameter + "\n")
        elif command == "ERROR":
            print(command + ": " + parameter + "\n")
        elif command == "LIST":
            (number, _, names) = parameter.strip().partition(' ')
            namesList = names.split()
            print(number + " clients active:")
            for i in namesList:
                print("- " + i)
            print()
        else:
            print(message + "\n")
        return True

    def onConnect(self, socket):
        print("\nOpened My Client")

    def onDisconnect(self, socket):
        print("Closed My Client")


# Parse the IP address and port you wish to connect to.
ip = sys.argv[1]
port = int(sys.argv[2])
screenName = sys.argv[3]

try:
    # Create an IRC client.
    client = IRCClient()

    # Start server
    client.start(ip, port)

    # *** register your client here, e.g. ***
    message="REGISTER "+screenName
    client.send(message.encode())

    while client.isRunning():
        try:
            command = input("").strip()
            client.send(command.encode())

        except (KeyboardInterrupt, OSError):
            try:
                message="DISCONNECT"
                client.send(message.encode())
                client.stop()
            except:
                client.stop()

        except:
            print("UNKNOWN ERROR: Closing the client")
            try:
                message="DISCONNECT"
                client.send(message.encode())
            except:
                pass
            client.stop()

    client.stop()

except:
    print("\nMy Server is not running or there was a problem when trying to connect to it\n")


