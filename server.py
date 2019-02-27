import socket
import time
import os
from os.path import isfile, join, abspath, exists
import logging
from pathlib import Path

filesystem_dir = "/Volumes/DATA/Projects/miniprint/filesystem"
log_location = Path("./miniprint.log")

def get_parameters(command):
    request_parameters = {}
    for item in command.split(" "):
        if ("=" in item):
            request_parameters[item.split("=")[0]] = item.split("=")[1]

    return request_parameters


def command_fsdirlist(conn, logger, request):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])
    logger.info("[Receive] FSDIRLIST : " + request_parameters["NAME"])

    requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
    logger.debug("Requested dir: '" + requested_dir + "'")
    resolved_dir = abspath(filesystem_dir + requested_dir)
    logger.debug("resolved_dir: " + resolved_dir)
    if resolved_dir[0:len(filesystem_dir)] != filesystem_dir:
        logger.warn("[Attack] Path traversal attack attempted! Directory requested: " + str(resolved_dir))
        resolved_dir = filesystem_dir

    return_entries = ""
    for entry in os.listdir(resolved_dir):
        if isfile(join(resolved_dir, entry)):
            return_entries += "\r\n" + entry + " TYPE=FILE SIZE=0"  # TODO do size check
        else:
            return_entries += "\r\n" + entry + " TYPE=DIR"

    response=b'@PJL FSDIRLIST NAME="0:/" ENTRY=1\r\n. TYPE=DIR\r\n.. TYPE=DIR' + return_entries.encode('UTF-8') + delimiter
    logger.info("[Response] " + str(return_entries.encode('UTF-8')))
    conn.send(response)
    

def command_fsquery(conn, logger, request):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])
    logger.info("[Receive] FSQUERY : " + request_parameters["NAME"])

    requested_item = request_parameters["NAME"].replace('"', '').split(":")[1]
    logger.debug("Requested item: " + requested_item)
    resolved_item = abspath(filesystem_dir + requested_item)
    logger.debug("Resolved item: " + resolved_item)
    if resolved_item[0:len(filesystem_dir)] != filesystem_dir:
        logger.warn("[Attack] Path traversal attack attempted! Directory requested: " + str(resolved_item))
        resolved_item = filesystem_dir

    return_data = ''
    if exists(resolved_item):
        if isfile(resolved_item): # TODO: Get files to work and return "no" when item doesn't exist
            pass
        else:
            return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"

    response=b'@PJL FSQUERY ' + return_data.encode('UTF-8') + delimiter
    logger.info("[Response] " + str(return_data.encode('UTF-8')))
    conn.send(response)


def command_ustatusoff(conn, logger, request):
    logger.info("[Interpret] User wants status request. Sending empty ACK")
    logger.info("[Response] (empty ACK)")
    conn.send(b'')


def main():
    logger = logging.getLogger('miniprint')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_location)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    host = "localhost"
    port = 9100

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind((host,port))

    mySocket.listen(1)
    conn, addr = mySocket.accept()
    logger.info("Connection from:" + str(addr))

    while True:
        data = conn.recv(4096).strip()
        dataArray = data.decode('UTF-8').split('\r\n')
        dataArray[0] = dataArray[0].replace('\x1b%-12345X', '')
        logger.debug('[Receive-Raw] ' + str(dataArray))

        if (dataArray[0] == "@PJL USTATUSOFF"):
            command_ustatusoff(conn, logger, dataArray)
        elif (dataArray[0] == "@PJL INFO ID"):
            logger.info("[Interpret] User wants ID")
            response = b'@PJL INFO ID\r\n"hp LaserJet 4200"\r\n\x1b'+dataArray[1].encode('UTF-8')
            logger.info("[Response]  " + str(response))
            conn.send(response)
        elif (dataArray[0] == "@PJL INFO STATUS"):
            logger.info("[Interpret] User wants info-status")
            response = b'@PJL INFO STATUS\r\nCODE=10001\r\nDISPLAY="Ready"\r\nONLINE=TRUE'+dataArray[1].encode('UTF-8')
            logger.info("[Response] " + str(response))
            conn.send(response)
        elif (dataArray[0][0:14] == "@PJL FSDIRLIST"):
            command_fsdirlist(conn, logger, dataArray)
        elif (dataArray[0][0:12] == "@PJL FSQUERY"):
            command_fsquery(conn, logger, dataArray)
        else:
            logger.info("Unknown command:")
            logger.info(dataArray)
            conn.close()
            break

    conn.close()
    print("Connection with " + str(addr) + " closed")

if __name__ == '__main__':
    main()
