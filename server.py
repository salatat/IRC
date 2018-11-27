import socket
import sys
import select
import json
import string
from defines import LIST_ROOMS, CREATE_ROOM, JOIN_ROOM, LEAVE_ROOM, LIST_MEMBERS, MSG_ROOM, DISCONNECT, NEW_CONN, PRIV_MSG, SERVER_MSG
from defines import SRVR_LIST_ROOMS, SRVR_CREATE_ROOM, SRVR_JOIN_ROOM, SRVR_LEAVE_ROOM, SRVR_LIST_MEMBERS, SRVR_MSG_ROOM, SRVR_DISCONNECT
from defines import ERR_CREATE_ROOM, ERR_JOIN_ROOM, ERR_LEAVE_ROOM, ERR_LIST_MEMBERS, ERR_MSG_ROOM, ERR_PRIV_MSG
from defines import SRVR_ERR_CREATE_ROOM, SRVR_ERR_JOIN_ROOM, SRVR_ERR_LEAVE_ROOM, SRVR_ERR_LIST_MEMBERS, SRVR_ERR_MSG_ROOM, SRVR_ERR_PRIV_MSG
from defines import HOST, PORT

class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # Dictionary pairing sockets to their client names
        # e.g. {"SOCKET_A":"CLIENT_NAME_A"}
        self.clients = {}
        # Dictionary pairing rooms to a list of tuples containing client socket and names
        # e.g. {"ROOM_NAME":[("SOCKET_A","CLIENT_NAME_A"),("SOCKET_B","CLIENT_NAME_B")]}
        self.rooms = {}
    #__init__()

    def start_server(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.host, self.port))

        # Add serverSocket to client list to include incoming client connections as part of
        # server's main listening loop and also stdin to capture server commands
        self.clients[self.serverSocket] = "SERVER_SOCKET"
        self.clients[sys.stdin]         = "SERVER_INPUT"
 
        self.serverSocket.listen(1)
        print("[SERVER] LISTENING HOST["+str(self.host)+"] PORT["+str(self.port)+"]")
        print("Type -help for a list of available commands")
        while True:
            try:
                read, write, error = select.select(list(self.clients.keys()), [], [])
            except socket.error as err:
                print("[SERVER] ERROR [read, write from client list]: "+err)
                continue
            try:
                for r in read:
                    # Handle new connections
                    if r == self.serverSocket:
                        try:
                            clientSocket, clientAddr = self.serverSocket.accept()
                        except socket.error as err:
                            print("ERROR [accepting client connection]: "+err)
                            break

                        # For initial connection, pair socket with sock (assume name comes next from this client)
                        self.clients[clientSocket] = clientSocket

                    # Handle server's stdin
                    elif r == sys.stdin:
                        server_input = (sys.stdin.readline()).lower()
                        if "-help" in server_input:
                            send_flag = False
                            print("Available commands:")
                            print("\t-disconnect\tDisconnects from server and quits.")
                            print("\t-quit\tDisconnects from server and quits.")
                            print("\t-help\tPrint this menu.")
                        elif "-disconnect" in server_input:
                            self.disconnect_all_clients()
                        elif "-quit" in server_input:
                            self.disconnect_all_clients()
                            print("[SERVER] Closing connection...")
                            self.serverSocket.close()
                            print("[SERVER] Exiting...")
                            return
                        else:
                            print("Invalid command. Type -help to list available commands.")
                        #if

                    # Otherwise, handle incoming data from clients
                    else:
                        client_data = r.recv(2048)

                        if not client_data:
                            print("[SERVER] username["+self.clients[r]+"] disconnected...")
                            self.disconnect_client(r)
                            continue
                        #if

                        data             = json.loads(client_data.decode("utf-8")); 
                        message_status   = data["status"]
                        message_username = data["username"] 
                        message          = data["message"]
                        # Sets name value to provided username for a new connection
                        if message_status & NEW_CONN:
                            print("[SERVER] Adding username["+str(message_username)+"] to socket["+str(r)+"]")
                            self.add_client_name(r, message_username)

                        # Provide a space delineated list of room names
                        elif message_status & LIST_ROOMS:
                            print("[SERVER] Listing rooms for username["+str(message_username)+"]")
                            self.list_rooms(r)

                        # Create a new room and add the user to it
                        elif message_status & CREATE_ROOM:
                            print("[SERVER] Created room["+str(message)+"] and added username["+str(message_username)+"]")
                            self.create_room(r, message_username, message)

                        # Add a user to a room
                        elif message_status & JOIN_ROOM:
                            print("[SERVER] Added username["+str(message_username)+"] to room["+str(message)+"]")
                            self.join_room(r, message_username, message)

                        # Remove a user from a room
                        elif message_status & LEAVE_ROOM:
                            print("[SERVER] Removing user["+str(message_username)+"] from room["+str(message)+"]")
                            self.leave_room(r, message_username, message)

                        # Provide a space dileneated list of users in a given room
                        elif message_status & LIST_MEMBERS:
                            print("[SERVER] Listing usernames for room["+str(message)+"]")
                            self.list_members(r, message)

                        # Pass a message from one client to all other clients in a room
                        # iff the messaging client is also in that room
                        elif message_status & MSG_ROOM:
                            temp = message.split("#RMS#", 1)
                            temp[0] = temp[0][:0] + temp[0][1:]
                            rooms = temp[0].split("#")
                            message = temp[1]
                            for room_name in rooms:
                                print("[SERVER] Sending message from username["+str(message_username)+"] to room["+str(room_name)+"]")
                                self.message_room(r, message_username, message, room_name)
                            #for

                        elif message_status & PRIV_MSG:
                            temp = message.split("#RMS#", 1)
                            print("[SERVER] username["+str(self.clients[r])+"] sending private message to ["+str(temp[0])+"]")
                            self.message_user(r, message_username, temp[1], temp[0])

                        # Handle a disconnecting client by cleaning up necessary structures
                        # and notify other users that were in the same room(s) of the disconnect
                        elif message_status & DISCONNECT:
                            print("[SERVER] username["+self.clients[r]+"] disconnected...")
                            self.disconnect_client(r)
                        #if
                    #if
                #for
            except Exception as generalErr:
                print("ERROR: "+str(generalErr))
                continue
        #while

    def add_client_name(self, clientSocket, username):
        self.clients[clientSocket] = username
    #add_client_name()

    def list_rooms(self, clientSocket):
        message = ""
        # Rooms are separated by space
        for room in self.rooms:
            message += room+" "
        #for

        data = {
            "status": SRVR_LIST_ROOMS,
            "username": "SERVER",
            "message": message
        }
        clientSocket.send(json.dumps(data).encode("utf-8"))
    #list_rooms()

    def create_room(self, clientSocket, username, room_name):
        status = SRVR_CREATE_ROOM
        message = "New room ["+str(room_name)+"] created and joined."

        if room_name in self.rooms:
            status = SRVR_ERR_CREATE_ROOM
            message = "Room: ["+str(room_name)+"] already exists."
        else:
            self.rooms[room_name] = []
            self.rooms[room_name].append((clientSocket, username))
        #if

        data = {
            "status": status,
            "username": "SERVER",
            "message": message
        }
        clientSocket.send(json.dumps(data).encode("utf-8"))
    #create_room()

    def join_room(self, clientSocket, username, room_name):
        status = SRVR_JOIN_ROOM
        message = ""
        if room_name not in self.rooms:
            status = SRVR_ERR_LEAVE_ROOM
            message = "Room: ["+str(room_name)+"] does not exist."
        else:
            message = "Room ["+str(room_name)+"] joined."
            self.rooms[room_name].append((clientSocket, username))
        #if

        data = {
            "status": status,
            "username": "SERVER",
            "message": message
        }
        clientSocket.send(json.dumps(data).encode("utf-8"))
    #join_room()

    def leave_room(self, clientSocket, username, room_name):
        status = SRVR_LEAVE_ROOM
        message = "You have left room: ["+str(room_name)+"]."

        if room_name not in self.rooms:
            status = SRVR_ERR_LEAVE_ROOM
            message = "The room: ["+str(room_name)+"] does not exist."
        else:
            self.rooms[room_name].remove((clientSocket, username))
        #if

        data = {
            "status": status,
            "username": "SERVER",
            "message": message
        }
        clientSocket.send(json.dumps(data).encode("utf-8"))
    #leave_room()

    def list_members(self, clientSocket, room_name):
        message = room_name+"#RM#"
        status = SRVR_LIST_MEMBERS

        if room_name in self.rooms:
            clients = self.rooms.get(room_name)
            for client in clients:
                message += str(client[1])+" "
            #for
        else:
            status = SRVR_ERR_LIST_MEMBERS
            message = "Room: ["+str(room_name)+"] does not exist."
        #if

        data = {
            "status": status,
            "username": "SERVER",
            "message": message
        }
        clientSocket.send(json.dumps(data).encode("utf-8"))
    #list_members()

    def message_room(self, clientSocket, username, message, room_name):
        data = {
            "status": MSG_ROOM,
            "username": username,
            "message": room_name+"#RM#"+message
        }
        if room_name in self.rooms:
            clients = self.rooms.get(room_name)
            if (clientSocket, username) not in clients:
                data["status"]   = SRVR_ERR_MSG_ROOM
                data["username"] = "SERVER"
                data["message"]  = "You are not in room: ["+str(room_name)+"]."
                print(data)
                clientSocket.send(json.dumps(data).encode("utf-8"))
                return
            #if
            for client in clients:
                if client[0] != clientSocket:
                    client[0].send(json.dumps(data).encode("utf-8"))
                #if
            #for
        else:
            data["status"]   = SRVR_ERR_MSG_ROOM
            data["username"] = "SERVER"
            data["message"]  = "Room: ["+room_name+"] does not exist."
            clientSocket.send(json.dumps(data).encode("utf-8"))
        #if
    #message_room()

    def message_user(self, clientSocket, username, message, to_username):
        data = {
            "status": PRIV_MSG,
            "username": username,
            "message": "PRIVATE MESSAGE#RM#"+message
        }

        to_user_exists = False

        for client,name in self.clients.items():
            if to_username == name and client != clientSocket:
                to_user_exists = True
                client.send(json.dumps(data).encode("utf-8"))
                print("[SERVER] Message sent from ["+username+"] to ["+to_username+"]")
            #if
        #for

        if not to_user_exists:
            print("user not found")
            data["status"]   = SRVR_ERR_PRIV_MSG
            data["username"] = "SERVER"
            data["message"]  = "Username: ["+to_username+"] not found."
            clientSocket.send(json.dumps(data).encode("utf-8"))
        #if
    #message_user()

    def disconnect_client(self, clientSocket):
        # Remove client from all rooms and message others in that room
        # that this client disconnect
        in_room = False
        client_name = ""

        for room, clients in self.rooms.items():
            for client in clients:
                if clientSocket == client[0]:
                    in_room = True
                    client_name = client[1]
                    clients.remove((client[0], client[1]))
                #if
            #for

            # If client was in room, message other clients of the disconnect
            if in_room == True:
                for client in clients:
                    data = {
                        "status": DISCONNECT,
                        "username": client_name,
                        "message": "["+str(room)+"] "+str(client_name)+" has disconnected."
                    }
                    client[0].send(json.dumps(data).encode("utf-8"))
                #for
            #if
        #for

        # Remove client from client list
        clientSocket.close()
        del self.clients[clientSocket]
    #disconnect_client()

    def disconnect_all_clients(self):
        data = {
            "status": SRVR_DISCONNECT,
            "username": "SERVER",
            "message": "You have been disconnected from the server."
        }
        # Disconnect clients
        for client,username in self.clients.items():
            if client != sys.stdin and client != self.serverSocket:
                client.send(json.dumps(data).encode("utf-8"))
                client.close()
            #if
        #for

        # Cleanup clients and rooms structures
        self.clients.clear()
        self.rooms.clear()

        # Reinclude client socket and stdin after getting cleared
        self.clients[self.serverSocket] = "SERVER_SOCKET"
        self.clients[sys.stdin]         = "SERVER_INPUT"
    #disconnect_all_clients()

def main():
    server = Server(HOST, PORT)
    server.start_server()
    del server
    return 0
#main()

if __name__ == "__main__":
    main()
#if
