import socketserver
import time
import os
from os.path import isfile, join, abspath, exists
from pathlib import Path
import logging
import select
import sys
import traceback
from printer import Printer


log_location = "./miniprint.log"

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
        printer = Printer(logger)
        
        emptyRequest = False
        while emptyRequest == False:
            
            # Wait a maximum of conn_timeout seconds for another request
            # If conn_timeout elapses without request, close the connection
            ready = select.select([self.request], [], [], conn_timeout)
            if not ready[0]:
                break
            
            try:
                self.data = self.request.recv(1024).strip()
            except Exception as e:
                logger.error("handle - receive - Error receiving data - possible port scan")
                emptyRequest = True
                break

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
                        response += printer.command_echo(command)
                    elif command == "USTATUSOFF":
                        response += printer.command_ustatusoff(command)
                    elif command == "INFO ID":
                        response += printer.command_info_id(command)
                    elif command == "INFO STATUS":
                        response += printer.command_info_status(command)
                    elif command[0:9] == "FSDIRLIST":
                        response += printer.command_fsdirlist(command)
                    elif command[0:7] == "FSQUERY":
                        response += printer.command_fsquery(command)
                    elif command[0:7] == "FSMKDIR":
                        response += printer.command_fsmkdir(command)
                    elif command[0:6] == "RDYMSG":
                        response += printer.command_rdymsg(command)
                    else:
                        logger.error("handle - cmd_unknown - " + str(command))

                logger.info("handle - response - " + response)
                self.request.sendall(response.encode('UTF-8')) 

            except Exception as e:
                tb = sys.exc_info()[2]
                traceback.print_tb(tb)
                logger.error("handle - error_caught - " + str(e))

        logger.info("handle - close_conn - " + self.client_address[0])

if __name__ == "__main__":
    HOST, PORT = "localhost", 9100
    
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.allow_reuse_address = True
    logger.info("main - start - Server started")
    server.serve_forever()
