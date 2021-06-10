import socket
import argparse
import signal
import sys
import random
from threading import Thread

clients = []


def signal_handler(signal, frame):
    print("terminating server...", flush=True)
    sys.exit()


class Client:

    def __init__(self, ip, port, name, nat_ip, nat_port):
        self.ip = ip
        self.name = name
        self.port = port
        self.nat_ip = nat_ip
        self.nat_port = nat_port


class ClientThread(Thread):

    def __init__(self, data, addr, sock, log):
        Thread.__init__(self)
        self.data = data
        self.addr = addr
        self.sock = sock
        self.log = log

    def run(self):

        DATA_NEW = self.data.decode('utf-8').split()

        # registration process
        if DATA_NEW[0] == 'register':

            CLIENT_IP = str(self.addr[0])
            CLIENT_PORT = int(self.addr[1])
            CLIENT_NAME = DATA_NEW[1]
            CLIENT_NAT_PORT = random.randrange(6000, 21000)
            CLIENT_NAT_IP = "127.0.0.1"

            SUCC_REG = ("welcome " + CLIENT_NAME).encode('utf-8')
            self.sock.sendto(SUCC_REG, (CLIENT_IP, CLIENT_PORT))

            MESSAGE = "%s | %s, %s | %s, %s\n" % (CLIENT_NAME, CLIENT_IP, CLIENT_PORT, CLIENT_NAT_IP, CLIENT_NAT_PORT)
            self.log.write(MESSAGE)

            newClient = Client(CLIENT_IP, CLIENT_PORT, CLIENT_NAME, CLIENT_NAT_IP, CLIENT_NAT_PORT)
            clients.append(newClient)

        elif DATA_NEW[0] == "sendto":

            MESSAGE = " ".join(DATA_NEW).encode('utf-8')

            for x in clients:
                if x.port == addr[1]:
                    NEW_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    NEW_SOCK.bind((x.nat_ip, x.nat_port))
                    NEW_SOCK.sendto(MESSAGE, (SERVER_IP, SERVER_PORT))

                    data = NEW_SOCK.recv(1024)
                    NEW_SOCK.sendto(data, (x.ip, x.port))
                    NEW_SOCK.close()


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
    parser.add_argument("-m", required=True
                        , help="Port the NAT is running on.")
    parser.add_argument("-d", required=True
                        , help="Server IP Address.")

    args = parser.parse_args()

    IP = "127.0.0.1"
    NAT_PORT = int(args.m)
    SERVER_PORT = args.p
    SERVER_IP = args.d

    logfile = open(args.l, "a")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, NAT_PORT))

    threads = []
    while True:
        data, addr = sock.recvfrom(1024)
        newThread = ClientThread(data, addr, sock, logfile)
        newThread.daemon = True
        newThread.start()
        threads.append(newThread)
