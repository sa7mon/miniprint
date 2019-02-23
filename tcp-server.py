import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        dataArray = self.data.decode('UTF-8').split('\r\n')
        print(dataArray)
        dataArray[0] = dataArray[0].replace('\x1b%-12345X', '')
        print(dataArray)

        if (dataArray[0] == "@PJL USTATUSOFF"):
            print("Received status request. Sending empty ACK")
            self.request.send(b'')

        #print(self.data.decode('UTF-8'))
        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "localhost", 9100

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.allow_reuse_address = True
        server.serve_forever()
