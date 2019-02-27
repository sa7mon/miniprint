import socketserver
import time
import os
from os.path import isfile, join, abspath, exists
from pathlib import Path
import logging
import select

filesystem_dir = "/home/ubuntu/workspace/filesystem"
# log_location = Path("./miniprint.log")

conn_timeout = 120 # Seconds to wait for request before closing connection

logger = logging.getLogger('miniprint')
logger.setLevel(logging.DEBUG)
# # create file handler which logs even debug messages
# # fh = logging.FileHandler(log_location)
# # fh.setLevel(logging.DEBUG)
# # create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# # create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)5s - %(message)s')
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
    requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
    logger.info("fsdirlist - request - Requested dir: '" + requested_dir + "'")
    resolved_dir = abspath(filesystem_dir + requested_dir)
    logger.debug("fsdirlist - request - resolved_dir: " + resolved_dir)
    if resolved_dir[0:len(filesystem_dir)] != filesystem_dir:
        logger.warn("fsdirlist - attack - Path traversal attack attempted! Directory requested: " + str(resolved_dir))
        resolved_dir = filesystem_dir

    return_entries = ""
    for entry in os.listdir(resolved_dir):
        if isfile(join(resolved_dir, entry)):
            return_entries += "\r\n" + entry + " TYPE=FILE SIZE=0"  # TODO do size check
        else:
            return_entries += "\r\n" + entry + " TYPE=DIR"

    response=b'@PJL FSDIRLIST NAME="0:/" ENTRY=1\r\n. TYPE=DIR\r\n.. TYPE=DIR' + return_entries.encode('UTF-8') + delimiter
    logger.info("fsdirlist - response - " + str(return_entries.encode('UTF-8')))
    self.request.sendall(response)
    

def command_fsquery(self, request):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])
    logger.info("fsquery - request - " + request_parameters["NAME"])

    requested_item = request_parameters["NAME"].replace('"', '').split(":")[1]
    logger.debug("fsquery - request - requested_item: " + requested_item)
    resolved_item = abspath(filesystem_dir + requested_item)
    logger.debug("fsquery - request - resolved_item: " + resolved_item)
    if resolved_item[0:len(filesystem_dir)] != filesystem_dir:
        logger.warn("fsquery - attack - Path traversal attack attempted! Directory requested: " + str(resolved_item))
        resolved_item = filesystem_dir

    return_data = ''
    if exists(resolved_item):
        if isfile(resolved_item): # TODO: Get files to work and return "no" when item doesn't exist
            pass
        else:
            return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"

    response=b'@PJL FSQUERY ' + return_data.encode('UTF-8') + delimiter
    logger.info("fsquery - response - " + str(return_data.encode('UTF-8')))
    self.request.sendall(response)


def command_ustatusoff(self, request):
    logger.info("ustatusoff - request - Request received")
    logger.info("ustatusoff - response - Sending empty reply")
    self.request.sendall(b'')


def command_info_id(self, request, printer):
    logger.info("info_id - request - ID requested")
    response = b'@PJL INFO ID\r\n' + printer.id + '\r\n\x1b' + request[1].encode('UTF-8')
    logger.info("info_id - response - " + str(response))
    self.request.sendall(response)


def command_info_status(self, request):
    logger.info("info_status - request - Client requests status")
    response = b'@PJL INFO STATUS\r\nCODE=10001\r\nDISPLAY="Ready"\r\nONLINE=TRUE'+request[1].encode('UTF-8')
    logger.info("info_status - response - " + str(response))
    self.request.sendall(response)


class Printer:
    # kind = 'canine'         # class variable shared by all instances

    def __init__(self, id="hp LaserJet 4200", code=10001, ready_msg="Ready", 
                    online=True):
        self.id = id
        self.code = code
        self.ready_msg = ready_msg
        self.online = online


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        logger.info("handle - open_conn - " + self.client_address[0])
        printer = Printer()
        
        emptyRequest = False
        while emptyRequest == False:
            
            # Wait a maximum of conn_timeout seconds for another request
            # If conn_timeout elapses without request, close the connection
            ready = select.select([self.request], [], [], conn_timeout)
            if not ready[0]:
                break
            
            self.data = self.request.recv(1024).strip()
            dataArray = self.data.decode('UTF-8').split('\r\n')

            dataArray[0] = dataArray[0].replace('\x1b%-12345X', '')
            logger.debug('handle - request - ' + str(dataArray))

            if dataArray[0] == '':  # If we're sent an empty request, close the connection
                emptyRequest = True
                break

            try:
                if (dataArray[0] == "@PJL USTATUSOFF"):
                    command_ustatusoff(self, dataArray)
                elif (dataArray[0] == "@PJL INFO ID"):
                    command_info_id(self, dataArray, printer=printer)
                elif (dataArray[0] == "@PJL INFO STATUS"):
                    command_info_status(self, dataArray)
                elif (dataArray[0][0:14] == "@PJL FSDIRLIST"):
                    command_fsdirlist(self, dataArray)
                elif (dataArray[0][0:12] == "@PJL FSQUERY"):
                    command_fsquery(self, dataArray)
                else:
                    logger.error("handle - cmd_unknown - " + str(dataArray))

            except Exception as e:
                logger.error("handle - error_caught - " + str(e))

        logger.info("handle - close_conn - " + self.client_address[0])

if __name__ == "__main__":
    HOST, PORT = "localhost", 9100
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.allow_reuse_address = True
        server.serve_forever()
