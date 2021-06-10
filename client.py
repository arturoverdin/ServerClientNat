import socket
import argparse
import signal
import sys

from threading import Thread


def signal_handler(signal, frame):
    print("terminating client...", flush=True)
    logfile.close()
    sys.exit()


class messageThread(Thread):

    def __init__(self, ip, name):
        Thread.__init__(self)
        self.ip = ip
        self.name = name

    def run(self):

        while True:
            data = sock.recv(1024)
            DATA_NEW = data.decode('utf-8').split()
            RECV = DATA_NEW[0]

            if RECV == "recvfrom":
                del DATA_NEW[0]
                del DATA_NEW[0]

                MESSAGE = " ".join(DATA_NEW)
                print("recvfrom " + MESSAGE, flush=True)


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", required=True
                        , help="Add port number to run server on."
                        , type=int)

    parser.add_argument("-s", required=True
                        , help="Chat server IP address.")

    parser.add_argument("-n", required=True
                        , help="Name of the client")

    parser.add_argument("-m"
                        , help="Port number client will run on."
                        , type=int)

    parser.add_argument("-l", required=True
                        , help="Name of output file.")

    args = parser.parse_args()

    UDP_IP = args.s
    UDP_PORT = args.p
    CLIENT_NAME = args.n
    CLIENT_PORT = args.m

    logfile = open(args.l, "a")
    logfile.write("connecting to the server 127.0.0.1 at port %s\n" % UDP_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    logfile.write("sending register message %s\n" % CLIENT_NAME)
    REGISTER = "register " + CLIENT_NAME
    REGISTER = REGISTER.encode('utf-8')

    sock.sendto(REGISTER, (UDP_IP, UDP_PORT))

    data, addr = sock.recvfrom(1024)
    DATA_NEW = data.decode('utf-8')
    SUCC_REG = "welcome " + CLIENT_NAME

    if DATA_NEW == SUCC_REG:
        print("connected to server and registered " + CLIENT_NAME, flush=True)
        newThread = messageThread(UDP_IP, CLIENT_NAME)
        newThread.daemon = True
        newThread.start()

        while True:
            RAW_MESSAGE = input("")
            PROC_MESSAGE = RAW_MESSAGE.split()

            if RAW_MESSAGE == 'exit':
                print("terminating client...", flush=True)
                logfile.close()
                break
            elif PROC_MESSAGE[0] == 'sendto':
                logfile.write("sending %s,%s %s\n" % (UDP_IP, UDP_PORT, " ".join(PROC_MESSAGE[1:len(PROC_MESSAGE)])))
                MESSAGE = RAW_MESSAGE.encode('utf-8')
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))