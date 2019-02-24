import socket
import time
import os
from os.path import isfile, join, abspath, exists

filesystem_dir = "/mnt/hgfs/faux-printer/filesystem"


def get_parameters(command):
    request_parameters = {}
    for item in command.split(" "):
        if ("=" in item):
            request_parameters[item.split("=")[0]] = item.split("=")[1]

    return request_parameters


def command_fsdirlist(conn, request):
    # request - ['@PJL FSDIRLIST NAME="0:/" ENTRY=1 COUNT=65535', '@PJL ECHO DELIMITER22148', '', '\x1b%-12345X']
    delimiter = request[1].encode('UTF-8')
    
    request_parameters = get_parameters(request[0])

    requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
    print("Requested dir: '" + requested_dir + "'")
    resolved_dir = abspath(filesystem_dir + requested_dir)
    print("resolved_dir: ", resolved_dir)
    if resolved_dir[0:len(filesystem_dir)] != filesystem_dir:
        print("WARNING: Path traversal attack attempted")
        resolved_dir = filesystem_dir

    return_entries = ""
    for entry in os.listdir(resolved_dir):
        if isfile(join(resolved_dir, entry)):
            return_entries += "\r\n" + entry + " TYPE=FILE SIZE=0"  # TODO do size check
        else:
            return_entries += "\r\n" + entry + " TYPE=DIR"

    response=b'@PJL FSDIRLIST NAME="0:/" ENTRY=1\r\n. TYPE=DIR\r\n.. TYPE=DIR' + return_entries.encode('UTF-8') + delimiter
    print("[Response] " + str(response))
    conn.send(response)
    

def command_fsquery(conn, request):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])

    requested_item = request_parameters["NAME"].replace('"', '').split(":")[1]
    print("Requested item: ", requested_item)
    resolved_item = abspath(filesystem_dir + requested_item)
    print("Resolved item: ", resolved_item)
    if resolved_item[0:len(filesystem_dir)] != filesystem_dir:
        print("WARNING: Path traversal attack attempted")
        resolved_item = filesystem_dir

    return_data = ''
    if exists(resolved_item):
        if isfile(resolved_item):
            pass
        else:
            return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"

    response=b'@PJL FSQUERY ' + return_data.encode('UTF-8') + delimiter
    print("[Response] " + str(response))
    conn.send(response)

def main():
    host = "localhost"
    port = 9100

    mySocket = socket.socket()
    mySocket.bind((host,port))

    mySocket.listen(1)
    conn, addr = mySocket.accept()
    print("Connection from:" + str(addr))

    while True:
        data = conn.recv(1024).strip()
        dataArray = data.decode('UTF-8').split('\r\n')
        dataArray[0] = dataArray[0].replace('\x1b%-12345X', '')
        print('[Receive] ' + str(dataArray))

        if (dataArray[0] == "@PJL USTATUSOFF"):
            print("[Interpret] User wants status request. Sending empty ACK")
            conn.send(b'')
        elif (dataArray[0] == "@PJL INFO ID"):
            print("[Interpret] User wants ID")
            response = b'@PJL INFO ID\r\n"hp LaserJet 4200"\r\n\x1b'+dataArray[1].encode('UTF-8')
            print("[Response]  " + str(response))
            conn.send(response)
        elif (dataArray[0] == "@PJL INFO STATUS"):
            print("[Interpret] User wants info-status")
            response = b'@PJL INFO STATUS\r\nCODE=10001\r\nDISPLAY="Ready"\r\nONLINE=TRUE'+dataArray[1].encode('UTF-8')
            print("[Response] " + str(response))
            conn.send(response)
        elif (dataArray[0][0:14] == "@PJL FSDIRLIST"):
            command_fsdirlist(conn, dataArray)
        elif (dataArray[0][0:12] == "@PJL FSQUERY"):
            command_fsquery(conn, dataArray)
        else:
            print("Unknown command:")
            print(dataArray)
            conn.close()
            break

    conn.close()
    print("Connection with " + str(addr) + " closed")

if __name__ == '__main__':
    main()

