from socket import *
import signal, sys
from multiprocessing import Process
from mysql import Database

HOST = "0.0.0.0"
PORT = 8086
ADDR = (HOST, PORT)
database = Database(database="dictionary")


def do_request(connfd):
    while True:
        data = connfd.recv(1024).decode()
        print(connfd.getpeername(), ":", data)
        if not data or data[0] == "E":
            do_exit(connfd)
        elif data[0] == "R":
            do_register(connfd, data)
        elif data[0] == "L":
            do_login(connfd, data)
        elif data[0] == "Q":
            do_query(connfd, data)
        elif data[0] == "H":
            do_history(connfd,data)


def do_register(connfd, data):
    name = data.split(" ")[1]
    password = data.split(" ")[2]
    if database.do_register(name, password):
        connfd.send(b"ok")
    else:
        connfd.send(b"fail")


def do_login(connfd, data):
    name = data.split(" ")[1]
    password = data.split(" ")[2]
    if database.do_login(name, password):
        connfd.send(b"ok")
    else:
        connfd.send(b"fail")


def do_exit(connfd):
    """
    child process exits
    :param connfd: connect socket
    :return: None
    """
    connfd.close()
    sys.exit()


def do_query(connfd, data):
    tmp = data.split(" ")
    name = tmp[1]
    word = tmp[2]
    database.insert_history(name, word)
    result = database.do_query(word)
    if result:
        message = f"{word}: {result}"
        connfd.send(message.encode())
    else:
        message = "there is no such word in the dictionary"
        connfd.send(message.encode())


def do_history(connfd,data):
    """
    obtain the history and send it to client
    :param connfd: connect socket
    :return: None
    """
    name=data.split(" ")[1]
    record = database.do_history(name)  # obtain the history
    if record:
        str_record = format_record(record)  # format the obtained record
        connfd.send(str_record.encode())  # send the record to client
    else:
        connfd.send(b"None")


def format_record(record):
    """
    format the record as a string
    :param record: searching record(tuple)
    :return: record(string)
    """
    str_record = ""
    for item in record:
        str_record += item[0] + "  "
        str_record += item[1] + "  "
        str_record += str(item[2])
        str_record += "#"
    return str_record


def main():
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    server.bind(ADDR)
    server.listen(3)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    while True:
        try:
            connfd, addr = server.accept()
            print("connect from", addr)
        except KeyboardInterrupt:
            sys.exit("server exits")
        except Exception as e:
            print(e)

        p = Process(target=do_request, args=(connfd,))
        p.daemon = True
        p.start()


if __name__ == "__main__":
    main()
