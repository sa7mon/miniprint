'''
miniprint - a medium interaction printer honeypot
Copyright (C) 2019 Dan Salmon - salmon@protonmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


import socketserver
from os.path import isfile, join
import logging
import select
import sys
import traceback
from printer import Printer
import argparse
import re


parser = argparse.ArgumentParser(description='''miniprint - a medium interaction printer honeypot
       by Dan Salmon: @BLTjetpack, github.com/sa7mon ''',
        prog='miniprint',
        usage='%(prog)s [-b,--bind HOST] [-l,--log-file FILE] [-t,--time-out TIME] [-h]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False)

o = parser.add_argument_group(title='optional arguments',
        description='''-b, --bind <host>       Bind the server to <host> (default: localhost)
-l, --log-file <file>   Save all logs to <file> (default: ./miniprint.log)
-t, --timeout <time>    Wait up to <time> seconds for commands before disconnecting client (default: 120)''')

o.add_argument('-b', '--bind', dest='host', default='localhost', help=argparse.SUPPRESS)
o.add_argument("-h", "--help", action="help", help="show this help message and exit")
o.add_argument('-l', '--log-file', dest='log_file', default='./miniprint.log', help=argparse.SUPPRESS)
o.add_argument('-t' ,'--timeout', type=int, dest='timeout', default=120, help=argparse.SUPPRESS)

args = parser.parse_args()

conn_timeout = args.timeout
log_location = args.log_file

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


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def parse_commands(self, text):
        '''
            Convert a string of commands to a list of commands. In the case of a print job (no @PJL prefix), append to the list untouched

            Examples:
                Input:  "@PJL USTATUSOFF\r\n@PJL INFO ID\r\n@PJL ECHO DELIMITER58494\r\n\r\n"
                Output: ['@PJL USTATUSOFF\r\n', '@PJL INFO ID\r\n', '@PJL ECHO DELIMITER58494\r\n\r\n']

                Input:  "This is my print job"
                Output: ['This is my print job']
        '''
        commands = []
        results = re.split('(@PJL)', text)
        results = [x for x in results if x]  # In case we have empty list elements
        
        for i, result in enumerate(results):
            if result == '@PJL':
                continue
            elif i > 0 and results[i-1] == '@PJL':
                commands.append('@PJL' + results[i])
            else:
                commands.append(results[i])

        return commands


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
            commands = self.parse_commands(request)

            logger.debug('handle - request - ' + str(request.encode('UTF-8')))

            if len(commands) == 0:  # If we're sent an empty request, close the connection
                emptyRequest = True
                break

            try:
                response = ''

                for command in commands:
                    command = command.lstrip()
                    
                    if command.startswith("@PJL "):
                        command = command[5:]
                        if printer.printing_raw_job:
                            printer.save_raw_print_job()

                        if command.startswith("ECHO"):
                            response += printer.command_echo(command)
                        elif command.startswith("USTATUSOFF"):
                            response += printer.command_ustatusoff(command)
                        elif command.startswith("INFO ID"):
                            response += printer.command_info_id(command)
                        elif command.startswith("INFO STATUS"):
                            response += printer.command_info_status(command)
                        elif command.startswith("FSDIRLIST"):
                            response += printer.command_fsdirlist(command)
                        elif command.startswith("FSQUERY"):
                            response += printer.command_fsquery(command)
                        elif command.startswith("FSMKDIR"):
                            response += printer.command_fsmkdir(command)
                        elif command.startswith("FSUPLOAD"):
                            response += printer.command_fsupload(command)
                        elif command.startswith("FSDOWNLOAD"):
                            response += printer.command_fsdownload(command)
                        elif command.startswith("RDYMSG"):
                            response += printer.command_rdymsg(command)
                        else:
                            logger.error("handle - cmd_unknown - " + str(command))
                    else:
                        response += printer.append_raw_print_job(command)

                logger.info("handle - response - " + str(response.encode('UTF-8')))
                self.request.sendall(response.encode('UTF-8'))

            except Exception as e:
                tb = sys.exc_info()[2]
                traceback.print_tb(tb)
                logger.error("handle - error_caught - " + str(e))

        if printer.printing_raw_job:
            printer.save_raw_print_job()
        logger.info("handle - close_conn - " + self.client_address[0])

if __name__ == "__main__":
    HOST, PORT = args.host, 9100

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.allow_reuse_address = True
    logger.info("main - start - Server started")
    server.serve_forever()
