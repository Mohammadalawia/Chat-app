import socket 
import threading
import time

username = input("Enter name:")

if username == 'admin':
    password = input("Enter password:")

client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
client.connect(('127.0.0.1', 44444))

stop_thread = False

def connecter():
    while True:
        global stop_thread

        if stop_thread:
            break

        try:
            message = client.recv(1024).decode('ascii')
            if message == 'Connection':
                client.send(username.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASSWORD':
                     client.send(password.encode('ascii'))
                     if client.recv(1024).decode('ascii') == 'REFUSED':
                        print('Connection was terminated!')
                        stop_thread = True

                elif next_message == 'BAN':
                    print("Connection refused! \nYou are banned.")
                    client.close()
                    stop_thread = True

            else:
                print(message)
        except:
            print("An error has occurd!")
            client.close()
            stop_thread = True
            break


def sender():
    while True:
        if stop_thread:
            break

        now = time.localtime()
        current_time = time.strftime("%H:%M" , now)
        message = f'[{current_time}]:{username} :{input("")}'

        if message[len(username)+10:].startswith('/'):
            if username == 'admin':
                if message[len(username)+10:].startswith('/kick'):
                    client.send(f"KICK {message[len(username)+10+6:]}".encode('ascii'))
                elif message[len(username)+10:].startswith('/ban'):
                    client.send(f"BAN {message[len(username)+10+5:]}".encode('ascii'))
            
            else:
                print("You're not admin!")
        else:       
            client.send(message.encode('ascii'))


connecter_thread = threading.Thread(target=connecter)
connecter_thread.start()

sender_thread = threading.Thread(target=sender)
sender_thread.start()