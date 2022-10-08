import sys
from ex2utils import Server

class EchoServer(Server):

    def onStart(self):
        self.numberClients = 0
        self.connections = []
        print("My server has started\n")

    def onStop(self):
        self.numberClients = 0
        self.connections = []
        print("My server has stopped")

    def onConnect(self, socket):
        socket.screenName = None
        self.numberClients += 1
        self.connections.append(socket)
        print("Client Connected", end="")
        print(" (%a clients active)\n" % (self.numberClients))
        socket.send(b"Client connected to My Server")

    def onMessage(self, socket, message):
        # This function takes two arguments: 'socket' and 'message'.
		#     'socket' can be used to send a message string back over the wire.
		#     'message' holds the incoming message string (minus the line-return).
	
        print("Command recieved: " + message)
        (command, _, parameter) = message.strip().partition(' ')

         # --- REGISTER COMMAND ---
        if command == "REGISTER":
            alreadyRegistered = False
            sentScreenName = parameter.encode()
            for skt in self.connections:
                if parameter == skt.screenName:
                    socket.send(b"ERROR ALREADY_REGISTERED_SCREENNAME: " + sentScreenName)
                    print("ERROR: Already registered screenName - " + parameter)
                    alreadyRegistered = True
            if alreadyRegistered is False:
                socket.screenName = parameter
                for skt in self.connections:
                    skt.send(b"REGISTER " + sentScreenName)
                print("Registered screenName: " + parameter)

        # --- DISCONNECT COMMAND ---
        elif command == "DISCONNECT":
            socket.send(b"Request to exit recieved")
            return False

        # --- CATCH UNREGISTERED SCREENNAME
        elif socket.screenName == None:
            socket.send(b"ERROR NOT_REGISTERED")
            print("ERROR: Not registered screenName")

        # --- MESSAGE EVERYONE COMMAND ---
        elif command == "MESSAGE":
            for skt in self.connections:
                # Dont send message to sender
                #if socket.screenName == skt.screenName:
                #    continue
                sentScreenName = socket.screenName.encode()
                sentMessage = parameter.encode()
                skt.send(b"MESSAGE " + sentScreenName + b" " + sentMessage)
            print(socket.screenName + " MESSAGED ALL " + parameter)

        # --- PRIVATE MESSAGE COMMAND ---
        elif command == "PRIVATE":
            (client, _, privateMessage) = parameter.strip().partition(' ')
            sentClient = client.encode()
            userFound = False
            for skt in self.connections:
                if client == skt.screenName:
                    sentScreenName = socket.screenName.encode()
                    sentMessage = privateMessage.encode()
                    skt.send(b"PRIVATE " + sentScreenName + b" " + sentClient + b" " + sentMessage)
                    print(socket.screenName + " PRIVATE " + client + " MSG=" + privateMessage)
                    userFound = True
                    socket.send(b"Succesfully sent message to " + sentClient)
            if userFound is False:
                socket.send(b"ERROR USER_NOT_FOUND " + sentClient)
                print(socket.screenName + " ERROR: User " + client + " not found")

        # --- LIST COMMAND ---
        elif command == "LIST":
            namesList = ""
            for skt in self.connections:
                if skt.screenName is None:
                    continue
                namesList += " "
                namesList += skt.screenName
                #namesList += "\n"

            sentMessage = str(self.numberClients).encode()
            sentList = namesList.encode()
            socket.send(b"LIST " + sentMessage + b" " + sentList)
            print(socket.screenName + " LISTED CLIENTS")

        # --- UNKNOWN COMMAND ERROR ---
        else:
            sentMessage = "ERROR UNKNOWN_COMMAND: " + message
            sentMessage = sentMessage.encode()
            socket.send(sentMessage)
            print("ERROR: UNKNOWN_COMMAND - " + message)
		
		# Signify all is well
        print("")
        return True
    
    def onDisconnect(self, socket):
        self.numberClients -= 1
        self.connections.remove(socket)
        socket.send(b"Disconnected from My Server")
        print("Client disconnected: " + str(socket.screenName), end="")
        print(" (%a clients active)\n" % (self.numberClients))
        return False


# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = EchoServer()

# Start server
server.start(ip, port)