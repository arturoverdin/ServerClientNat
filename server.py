import socket
import argparse
import signal
import sys
from threading import Thread


def signal_handler(signal, frame):
    print("terminating server...", flush=True)
    sys.exit()


class ClientThread(Thread):

    def __init__(self, data, addr, sock, log):
        Thread.__init__(self)
        self.log = log
        self.data = data
        self.addr = addr
        self.sock = sock

    def run(self):

        DATA_NEW = self.data.decode('utf-8').split()

        if DATA_NEW[0] == "sendto":

            del DATA_NEW[0]

            CLIENT_PORT = addr[1]
            CLIENT_IP = addr[0]
            MESSAGE = " ".join(DATA_NEW)

            MESSAGE = "recvfrom %s,%s %s \n" % (CLIENT_IP, CLIENT_PORT, MESSAGE)
            self.log.write(MESSAGE)
            print(MESSAGE, flush=True, end='')

            MESSAGE = MESSAGE.encode('utf-8')
            self.sock.sendto(MESSAGE, (CLIENT_IP, CLIENT_PORT))


if __name__ == "__main__":

    # takes care of the SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    # takes care of all the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", required=True
                        , help="Add port number to run server on."
                        , type=int)
    parser.add_argument("-l", required=True
                        , help="Name of output file.")

    args = parser.parse_args()

    IP = "127.0.0.1"
    UDP_PORT = args.p

    logfile = open(args.l, "a")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, UDP_PORT))

    logfile.write("server started on 127.0.0.1 at port %s\n" % UDP_PORT)
    print("server started on 127.0.0.1 at port %s" % UDP_PORT, flush=True)

    threads = []
    while True:
        data, addr = sock.recvfrom(1024)
        newThread = ClientThread(data, addr, sock, logfile)
        newThread.daemon = True
        newThread.start()
        threads.append(newThread)