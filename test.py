import json

#rooms = {}
#rooms["room1"]=[]
#rooms["room1"].append(("sock1","client1"))
#rooms["room1"].append(("sock2","client2"))
#
#print(rooms)
#print(rooms["room1"])
#
#for room,clients in rooms.items():
#    print(room)
#    for client in clients:
#        print(client[0]+" "+client[1])

#smsg = 1 << 15;
#n = 1 << 0;
#
#new = smsg | n
#
#msg = "hello"
#status = 1 << 16
#length = len(msg)
#name = "bob"
#
#packet = {
#    "status": new,
#    "username": name,
#    "length": length,
#    "message": msg
#}
#
#p = json.dumps(packet)
#s = json.loads(p)
#print(s["status"])

#message = "super_cool_stuff#rad_room#RMS# here is my message"
#temp = message.split("#RMS#", 1)
#rooms = temp[0].split("#")
#message = temp[1]
#
#print(rooms)
#print(message)

test1 = 1 << 15
test2 = 1 << 0
test3 = 1 << 4

test2 = test2 | test1
test3 = test3 | test1

print(test2)
print(test2 & test2)
print(test3)
print(test3 & test2)

if test2 & test2:
    print("2 and 2")
if test2 & test3:
    print("2 and 3")
