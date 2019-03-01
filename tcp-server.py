import socketserver
import time
import os
from os.path import isfile, join, abspath, exists
from pathlib import Path
import logging
import select
from pyfakefs import fake_filesystem
import sys
import traceback


log_location = Path("./miniprint.log")

conn_timeout = 120 # Seconds to wait for request before closing connection

logger = logging.getLogger('miniprint')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(log_location)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)5s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def create_fake_filesystem(fs):
    fs.create_dir("/PJL")
    fs.create_dir("/PostScript")
    fs.create_dir("/saveDevice/SavedJobs/InProgress")
    fs.create_dir("/saveDevice/SavedJobs/KeepJob")
    fs.create_dir("/webServer/default")
    fs.create_dir("/webServer/home")
    fs.create_dir("/webServer/lib")
    fs.create_dir("/webServer/objects")
    fs.create_dir("/webServer/permanent")
    fs.create_file("/webServer/default/csconfig")
    fs.create_file("/webServer/home/device.html")
    fs.create_file("/webServer/home/hostmanifest")
    fs.create_file("/webServer/lib/keys")
    fs.create_file("/webServer/lib/security")


def get_parameters(command):
    request_parameters = {}
    for item in command.split(" "):
        if ("=" in item):
            request_parameters[item.split("=")[0]] = item.split("=")[1]

    return request_parameters


def command_fsdirlist(self, request, printer):
    delimiter = request[1]
    request_parameters = get_parameters(request[0])
    requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]

    logger.debug("fsdirlist - request - Requested dir: '" + requested_dir + "'")
    return_entries = ""

    if printer.fos.path.exists(requested_dir):
        return_entries = ' ENTRY=1\r\n. TYPE=DIR\r\n.. TYPE=DIR'
        for entry in printer.fos.scandir(requested_dir):
            if entry.is_file():
                return_entries += "\r\n" + entry.name + " TYPE=FILE SIZE=0" #TODO check size
            elif entry.is_dir():
                return_entries += "\r\n" + entry.name + " TYPE=DIR"
    else:
        return_entries = "FILEERROR = 3" # "file not found"

    response = ('@PJL FSDIRLIST NAME="' + request_parameters['NAME'] + '"' + return_entries + delimiter).encode("UTF_8")
    logger.info("fsdirlist - response - " + str(return_entries.encode('UTF-8')))
    self.request.sendall(response)
    

def command_fsquery(self, request, printer):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])
    logger.info("fsquery - request - " + request_parameters["NAME"])

    requested_item = request_parameters["NAME"].replace('"', '').split(":")[1]
    logger.debug("fsquery - request - requested_item: " + requested_item)
    return_data = ''

    if (printer.fos.path.exists(requested_item)):
        a = printer.fs.get_object(requested_item)
        if type(a) == fake_filesystem.FakeFile:
            return_data = "NAME=" + request_parameters["NAME"] + " TYPE=FILE SIZE=0" # TODO Get actual file size
        elif type(a) == fake_filesystem.FakeDirectory:
            return_data = "NAME=" + request_parameters["NAME"] + " TYPE=DIR"
    else:
        return_data = "NAME=" + request_parameters["NAME"] + " FILEERROR=3\r\n" # File not found

    response=b'@PJL FSQUERY ' + return_data.encode('UTF-8') + delimiter
    logger.info("fsquery - response - " + str(return_data.encode('UTF-8')))
    self.request.sendall(response)


def command_fsmkdir(self, request, printer):
    delimiter = request[1].encode('UTF-8')
    request_parameters = get_parameters(request[0])
    requested_dir = request_parameters["NAME"].replace('"', '').split(":")[1]
    logger.info("fsmkdir - request - " + requested_dir)

    """
    Check if dir exists
        If it does, do nothing and return empty ACK
        If it doesn't, create dir and return empty ACK
    """
    if printer.fos.path.exists(requested_dir):
        pass
    else:
        printer.fs.create_dir(requested_dir)

    response=b''
    logger.info("fsquery - response - Sending empty response")
    self.request.sendall(response)


def command_ustatusoff(self, request):
    logger.info("ustatusoff - request - Request received")
    logger.info("ustatusoff - response - Sending empty reply")
    # self.request.sendall(b'')
    return ''


def command_info_id(self, request, printer):
    logger.info("info_id - request - ID requested")
    response = '@PJL INFO ID\r\n' + printer.id + '\r\n\x1b' + request[1]
    logger.info("info_id - response - " + str(response))
    # self.request.sendall(response)
    return response


def command_info_status(self, request, printer):
    logger.info("info_status - request - Client requests status")
    response = ('@PJL INFO STATUS\r\nCODE=' + str(printer.code) + '\r\nDISPLAY=' + printer.ready_msg + '\r\nONLINE=' + str(printer.online) + request[1]).encode('UTF-8')
    logger.info("info_status - response - " + str(response))
    self.request.sendall(response)


def command_echo(self, request):
    logger.info("echo - request - Received request for delimiter")
    response = ''
    response = "@PJL " + request
    response += '\x1b'
    logger.info("echo - response - Responding with: " + str(response.encode('UTF-8')))
    # self.request.sendall(response.encode('UTF-8')) 
    return response



class Printer:
    def __init__(self, id="hp LaserJet 4200", code=10001, ready_msg="Ready", 
                    online=True):
        self.id = id
        self.code = code
        self.ready_msg = ready_msg
        self.online = online
        self.fs = fake_filesystem.FakeFilesystem()
        self.fos = fake_filesystem.FakeOsModule(self.fs)
        create_fake_filesystem(self.fs)
        

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
            request = self.data.decode('UTF-8')
            request = request.replace('\x1b%-12345X', '')
            commands = request.split('@PJL')
            commands = [a for a in commands if a] # Filter out empty list items since split() returns an empty string

            logger.debug('handle - request - ' + str(request))

            if len(commands) == 0:  # If we're sent an empty request, close the connection
                emptyRequest = True
                break

            try:
                response = ''

                for command in commands:
                    command = command.strip()

                    if command[0:4] == "ECHO":
                        response += command_echo(self, command)
                    elif command == "USTATUSOFF":
                        response += command_ustatusoff(self, command)
                    elif command == "INFO ID":
                        response += command_info_id(self, command, printer=printer)
                    elif command == "INFO STATUS":
                        response += command_info_status(self, command, printer=printer)
                    elif (dataArray[0][0:14] == "@PJL FSDIRLIST"):
                        command_fsdirlist(self, dataArray, printer=printer)
                    elif (dataArray[0][0:12] == "@PJL FSQUERY"):
                        command_fsquery(self, dataArray, printer=printer)
                    elif (dataArray[0][0:12] == "@PJL FSMKDIR"):
                        command_fsmkdir(self, dataArray, printer=printer)
                    else:
                        logger.error("handle - cmd_unknown - " + str(dataArray))

                logger.info("handle - response - " + response)
                self.request.sendall(response.encode('UTF-8')) 

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
