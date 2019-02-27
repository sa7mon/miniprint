import socketserver
import time
import os
from os.path import isfile, join, abspath, exists
from pathlib import Path
import logging

filesystem_dir = "/home/ubuntu/workspace/filesystem"
# log_location = Path("./miniprint.log")


logger = logging.getLogger('miniprint')
logger.setLevel(logging.DEBUG)
# # create file handler which logs even debug messages
# # fh = logging.FileHandler(log_location)
# # fh.setLevel(logging.DEBUG)
# # create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# # create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# # fh.setFormatter(formatter)
ch.setFormatter(formatter)
# # add the handlers to the logger
# # logger.addHandler(fh)
logger.addHandler(ch)


def get_parameters(command):
    request_parameters = {}
    for item in command.split(" "):
        if ("=" in item):
            request_parameters[item.split("=")[0]] = item.split("=")[1]

    return request_parameters


def command_fsdirlist(self, request):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])
    print("[Receive] FSDIRLIST : " + request_parameters["NAME"])

    requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
    print("Requested dir: '" + requested_dir + "'")
    resolved_dir = abspath(filesystem_dir + requested_dir)
    print("resolved_dir: " + resolved_dir)
    if resolved_dir[0:len(filesystem_dir)] != filesystem_dir:
        print("[Attack] Path traversal attack attempted! Directory requested: " + str(resolved_dir))
        resolved_dir = filesystem_dir

    return_entries = ""
    for entry in os.listdir(resolved_dir):
        if isfile(join(resolved_dir, entry)):
            return_entries += "\r\n" + entry + " TYPE=FILE SIZE=0"  # TODO do size check
        else:
            return_entries += "\r\n" + entry + " TYPE=DIR"

    response=b'@PJL FSDIRLIST NAME="0:/" ENTRY=1\r\n. TYPE=DIR\r\n.. TYPE=DIR' + return_entries.encode('UTF-8') + delimiter
    print("[Response] " + str(return_entries.encode('UTF-8')))
    self.request.sendall(response)
    

def command_fsquery(self, request):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])
    print("[Receive] FSQUERY : " + request_parameters["NAME"])

    requested_item = request_parameters["NAME"].replace('"', '').split(":")[1]
    print("Requested item: " + requested_item)
    resolved_item = abspath(filesystem_dir + requested_item)
    print("Resolved item: " + resolved_item)
    if resolved_item[0:len(filesystem_dir)] != filesystem_dir:
        print("[Attack] Path traversal attack attempted! Directory requested: " + str(resolved_item))
        resolved_item = filesystem_dir

    return_data = ''
    if exists(resolved_item):
        if isfile(resolved_item): # TODO: Get files to work and return "no" when item doesn't exist
            pass
        else:
            return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"

    response=b'@PJL FSQUERY ' + return_data.encode('UTF-8') + delimiter
    print("[Response] " + str(return_data.encode('UTF-8')))
    self.request.sendall(response)


def command_ustatusoff(self, request):
    print("[Interpret] User wants status request. Sending empty ACK")
    print("[Response] (empty ACK)")
    self.request.sendall(b'')


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        logger.info("Connection from: " + self.client_address[0])

        emptyRequest = False
        while emptyRequest == False: # Keep listening for requests from this client until they send us nothing
            self.data = self.request.recv(1024).strip()
            dataArray = self.data.decode('UTF-8').split('\r\n')

            dataArray[0] = dataArray[0].replace('\x1b%-12345X', '')
            logger.debug('[Receive-Raw] ' + str(dataArray))

            if dataArray[0] == '':  # If we're sent an empty request, close the connection
                emptyRequest = True
                break

            try:
                if (dataArray[0] == "@PJL USTATUSOFF"):
                    command_ustatusoff(self, dataArray)
                elif (dataArray[0] == "@PJL INFO ID"):
                    logger.info("[Interpret] User wants ID")
                    response = b'@PJL INFO ID\r\n"hp LaserJet 4200"\r\n\x1b'+dataArray[1].encode('UTF-8')
                    logger.info("[Response]  " + str(response))
                    self.request.sendall(response)
                elif (dataArray[0] == "@PJL INFO STATUS"):
                    logger.info("[Interpret] User wants info-status")
                    response = b'@PJL INFO STATUS\r\nCODE=10001\r\nDISPLAY="Ready"\r\nONLINE=TRUE'+dataArray[1].encode('UTF-8')
                    logger.info("[Response] " + str(response))
                    self.request.sendall(response)
                elif (dataArray[0][0:14] == "@PJL FSDIRLIST"):
                    command_fsdirlist(self, dataArray)
                elif (dataArray[0][0:12] == "@PJL FSQUERY"):
                    command_fsquery(self, dataArray)
                else:
                    logger.error("Unknown command: " + str(dataArray))

            except Exception as e:
                logger.error("Caught error: " + str(e))

        logger.info("Connection closed from: " + self.client_address[0])

if __name__ == "__main__":
    HOST, PORT = "localhost", 9100
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.allow_reuse_address = True
        server.serve_forever()
