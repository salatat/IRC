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

class Client():
    def __init__(self, host, port, name):
        self.host = host
        self.port = port

        if len(str(name)) == 0:
            print("No username detected. Assigned username [Anonymous].")
            self.name = "Anonymous"
        else:
            self.name = str(name)
        #if
    #___init__()

    def start_client(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.clientSocket.connect((self.host, self.port))
        except socket.error as socketErr:
            print("ERROR: Unable to connect to server...")
            return -1
        print("Connected to server...")
        print("Type -help for a list of available commands")

        self.send_username()

        while True:
            try:
                read, write, error = select.select([sys.stdin, self.clientSocket], [], [])
            except socket.error as socketErr:
                print("ERROR: "+str(socketErr))
                continue

            for r in read:
                # Handle user input
                if r == sys.stdin:
                    send_flag = True
                    data = {
                        "status": "",
                        "username": self.name,
                        "message": ""
                    }

                    client_input = sys.stdin.readline()
                    # Check the first word for command type
                    tmp = client_input.replace("\n", "").split(" ", 1)
                    cmd = tmp[0].lower()

                    if cmd == "-help":
                        send_flag = False
                        print("Available commands:")
                        print("\t-msg r\u0332o\u0332o\u0332m\u0332s\u0332\tMust include at least one room name. Additional rooms must be separated by a space.")
                        print("\t\t\tYou will be prompted for message content. Can only message rooms you are currently in.")
                        print("\t\t\tMessage content size limited to 1024 characters.")
                        print("\t-priv u\u0332s\u0332e\u0332r\u0332n\u0332a\u0332m\u0332e\u0332\tDirectly message user. Functions similar to room messaging.")
                        print("\t-rooms\t\tList all current chat rooms on server.")
                        print("\t-members r\u0332o\u0332o\u0332m\u0332\u0332\tMust give one valid room name.")
                        print("\t-create r\u0332o\u0332o\u0332m\u0332\u0332\tMust give one room name. This will create a room and join that room.")
                        print("\t-leave r\u0332o\u0332o\u0332m\u0332\u0332\tMust give one valid room name. Removes client from chat room.")
                        print("\t-join r\u0332o\u0332o\u0332m\u0332\u0332\tMust give one valid room name. Adds client to chat room.")
                        print("\t-disconnect\tDisconnects from server and quits.")
                        print("\t-quit\tDisconnects from server and quits.")
                        print("\t-help\tPrint this menu.")
                        print("\t***NOTE: Room names cannot contain spaces or the following: #RMS#, #RM#, or any # characters")
                    elif cmd == "-msg":
                        data["status"] = MSG_ROOM
                        if "#" in tmp[1] or "#RM#" in tmp[1] or "RMS#" in tmp[1]:
                            print("Invalid room name: cannot contain spaces or the following: #RMS#, #RM#, or any # characters.")
                            send_flag = False
                        else:
                            rooms = tmp[1].split(" ")
                            for room in rooms:
                                data["message"] += "#"+room
                            #for
                            data["message"] += "#RMS#"
                            message_content = input("Message content (max 1024 characters): ")
                            if not message_content:
                                continue
                            #if
                            if len(message_content) > 1024:
                                print("Message exceeds 1024 characters. Message will not be sent.")
                                send_flag = False
                            else:
                                data["message"] += message_content
                            #if
                        #if
                    elif cmd == "-priv":
                        data["status"] = PRIV_MSG
                        if "#" in tmp[1] or "#RM#" in tmp[1] or "RMS#" in tmp[1]:
                            print("Invalid username: cannot contain spaces or the following: #RMS#, #RM#, or any # characters.")
                            send_flag = False
                        else:
                            data["message"] = str(tmp[1])+"#RMS#"
                            message_content = input("Message content (max 1024 characters): ")
                            if not message_content:
                                continue
                            #if
                            if len(message_content) > 1024:
                                print("Message exceeds 1024 characters. Message will not be sent.")
                                send_flag = False
                            else:
                                data["message"] += message_content
                            #if
                        #if
                    elif cmd == "-rooms":
                        data["status"]  = LIST_ROOMS
                    elif cmd == "-members":
                        data["status"]  = LIST_MEMBERS
                        if " " in tmp[1]  or "#" in tmp[1] or "#RM#" in tmp[1] or "RMS#" in tmp[1]:
                            print("Invalid room name: cannot contain spaces or the following: #RMS#, #RM#, or any # characters.")
                            send_flag = False
                        #if
                        data["message"] = str(tmp[1])
                    elif cmd == "-create":
                        data["status"]  = CREATE_ROOM
                        if " " in tmp[1]  or "#" in tmp[1] or "#RM#" in tmp[1] or "RMS#" in tmp[1]:
                            print("Invalid room name: cannot contain spaces or the following: #RMS#, #RM#, or any # characters.")
                            send_flag = False
                        #if
                        data["message"] = str(tmp[1]) 
                    elif cmd == "-leave":
                        data["status"]  = LEAVE_ROOM
                        if " " in tmp[1]  or "#" in tmp[1] or "#RM#" in tmp[1] or "RMS#" in tmp[1]:
                            print("Invalid room name: cannot contain spaces or the following: #RMS#, #RM#, or any # characters.")
                            send_flag = False
                        #if
                        data["message"] = str(tmp[1]) 
                    elif cmd == "-join":
                        data["status"]  = JOIN_ROOM
                        if " " in tmp[1]  or "#" in tmp[1] or "#RM#" in tmp[1] or "RMS#" in tmp[1]:
                            print("Invalid room name: cannot contain spaces or the following: #RMS#, #RM#, or any # characters.")
                            send_flag = False
                        #if
                        data["message"] = str(tmp[1]) 
                    elif cmd == "-disconnect" or cmd == "-quit":
                        data["status"]  = DISCONNECT
                        self.clientSocket.send(json.dumps(data).encode("utf-8"))
                        self.clientSocket.close()
                        return 0
                    else:
                        print("Invalid command. Type -help to list available commands.")
                        send_flag = False
                    #if
                    if send_flag == True:
                        self.clientSocket.send(json.dumps(data).encode("utf-8"))
                    #if
                # Handle incoming data from or forwarded by server
                else:
                    server_data = r.recv(2048)

                    if not server_data:
                        print("Server disconnected...")
                        self.clientSocket.close()
                        return 0
                    #if
                    try:
                        data = json.loads(server_data.decode("utf-8"))
                    except json.decoder.JSONDecodeError as jsonErr:
                        print("ERROR: "+str(jsonErr))
                        continue

                    message_status   = data["status"]
                    message_username = data["username"] 
                    message          = data["message"]

                    if message_status & LIST_ROOMS and message_status & SERVER_MSG:
                        self.parse_room_list(message)
                    elif message_status & CREATE_ROOM and message_status & SERVER_MSG:
                        print("["+str(message_username)+"] "+str(message))
                    elif message_status & JOIN_ROOM and message_status & SERVER_MSG:
                        print("["+str(message_username)+"] "+str(message))
                    elif message_status & LEAVE_ROOM and message_status & SERVER_MSG:
                        print("["+str(message_username)+"] "+str(message))
                    elif message_status & LIST_MEMBERS and message_status & SERVER_MSG:
                        print("listing members")
                        self.parse_member_list(message)
                    elif message_status & MSG_ROOM:
                        self.parse_message(message_username, message)
                    elif message_status & PRIV_MSG:
                        self.parse_priv_message(message_username, message)
                    elif message_status & DISCONNECT and message_status & SERVER_MSG:
                        print("Server disconnecting...")
                        self.clientSocket.close()
                        return 0
                    elif message_status & DISCONNECT:
                        print(message)
                    elif message_status & ERR_CREATE_ROOM and message_status & SERVER_MSG:
                        print("["+str(message_username)+"] "+message)
                    elif message_status & ERR_JOIN_ROOM and message_status & SERVER_MSG:
                        print("["+str(message_username)+"] "+message)
                    elif message_status & ERR_LEAVE_ROOM and message_status & SERVER_MSG:
                        print("["+str(message_username)+"] "+message)
                    elif message_status & ERR_LIST_MEMBERS and message_status & SERVER_MSGS:
                        print("["+str(message_username)+"] "+message)
                    elif message_status & ERR_MSG_ROOM and message_status & SERVER_MSG: 
                        print("["+str(message_username)+"] "+message)
                    elif message_status & ERR_PRIV_MSG and message_status & SERVER_MSG: 
                        print("["+str(message_username)+"] "+message)
                    else:
                        print("Received message with unknown status or type.")
                    #if
                #if
            #for
        #while
    #start_client()

    # Message expeted to be a space dilineated list of room names        
    def parse_room_list(self, message):
        if message:
            rooms = message.split(" ")
            print("Rooms:")
            for room in rooms:
                print("\t"+room)
            #for
        #if
    #parse_room_list()

    def parse_member_list(self, message):
        temp      = message.split("#RM#", 1)
        room      = temp[0]
        usernames = temp[1].split(" ")

        print("["+room+"] has the following users:")
        for username in usernames:
            print("\t"+username)
        #for
    #parse_member_list()
    
    def parse_priv_message(self, username, message):
        if username and message:
            temp = message.split("#RM#", 1)
            print(">>>["+temp[0]+"]["+username+"] "+ temp[1])
        #if
    #parse_priv_message()

    def parse_message(self, username, message):
        if username and message:
            temp = message.split("#RM#", 1)
            print("["+temp[0]+"]["+username+"] "+ temp[1])
        #if
    #parse_message()

    def send_username(self):
        data = {
            "status": NEW_CONN,
            "username": self.name,
            "message": ""
        }
        self.clientSocket.send(json.dumps(data).encode("utf-8"))
    #send_username()
#class Client()

def main():
    invalidUsername = True
    while invalidUsername:
        name = input("Choose a username: ")
        name.replace("\n", "")
        if " " in name or "#" in name or "#RM#" in name or "#RMS#" in name:
            print("Username cannot contain spaces or # characters.")
        else:
            invalidUsername = False
        #if
    #while

    client = Client(HOST, PORT, name)
    status = client.start_client()
    del client
    return status
#main()

if __name__ == "__main__":
    main()
#if
