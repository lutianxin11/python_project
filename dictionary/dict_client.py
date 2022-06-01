"""
function: according to the input of the client, sent corresponding
request to server, and receive feedback from server

structure:
    primary interface --> register, login, exit
    secondary interface --> search, history, logout
"""
import sys
from socket import *
from getpass import getpass  # available only on terminal

HOST = "0.0.0.0"
PORT = 8086
ADDR = (HOST, PORT)
CLIENT = socket()
CLIENT.connect(ADDR)
def do_register():
    while True:
        name=input("Name:")
        password=getpass()
        password1=getpass("again:")
        if password!=password1:
            print("the two password you entered are different.")
            continue
        if " " in name or " " in password:
            print("name and password can not contain space")
            continue
        message="R"+" "+name+" "+password
        CLIENT.send(message.encode())
        feedback=CLIENT.recv(128)
        if feedback.decode()=="ok":
            print("registered successfully")
            login(name)
        else:
            print(feedback.decode())
        return
def do_login():
    name=input("name:")
    password=getpass()
    message="L"+" "+name+" "+password
    CLIENT.send(message.encode())
    feedback=CLIENT.recv(128).decode()
    if feedback=="ok":
        print("login successfully")
        login(name)
def do_exit():
    CLIENT.send(b"E")
    sys.exit("client exit")
def login(name):
    while True:
        print("""
        ===============query==============
        1. search   2. history   3. logout
        ==================================
        """)
        cmd = input("select needed service by pressing corresponding number:")
        if cmd == "1":
            do_search(name)
        elif cmd == "2":
            do_history(name)
        elif cmd == "3":
            break
        else:
            print("please enter 1, 2 or 3:")
def do_search(name):
    while True:
        word=input("word(enter ## to exit):")
        if word=="##":
            break
        message="Q"+" "+ name+" "+ word
        CLIENT.send(message.encode())
        result=CLIENT.recv(2048).decode()
        print(result)

def do_history(name):
    message="H"+" "+name
    CLIENT.send(message.encode())
    history=CLIENT.recv(2048).decode()
    if history=="None":
        print("you don't have a record yet")
    else:
        list_history = history.split("#")
        for item in list_history:
            print(item)


def main():
    while True:
        print("""
        ==============welcome=============
         1. register   2. login   3. exit
        ==================================
        """)
        cmd = input("select needed service by pressing corresponding number:")
        if cmd == "1":
            do_register()
        elif cmd == "2":
            do_login()
        elif cmd == "3":
            do_exit()
        else:
            print("please enter 1, 2 or 3:")


if __name__ == "__main__":
    main()
