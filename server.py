import socket
import time

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
        else:
            # conn.close()
            # break
            print("Unknown command:")
            print(dataArray)
            conn.close()
            break

    conn.close()
    print("Connection with " + str(addr) + " closed")

if __name__ == '__main__':
    main()





