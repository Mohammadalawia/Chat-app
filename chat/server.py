import threading
import socket
import bcrypt
import time


HOST = '127.0.0.1'
PORT = 44444    

server= socket.socket(socket.AF_INET , socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = []


#-----------------------------------Connecting client to server ------------------------------------------
def connecter():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('Connection'.encode('ascii'))
        username = client.recv(1024).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()
            if username+'\n' in bans:
                client.send('BAN'.encode('ascii'))
                client.close()
                continue


        if username =='admin':
            client.send('PASSWORD'.encode('ascii'))
            password = client.recv(1024).decode('ascii') 

            if check_password(password):
                client.send('Access denied.'.encode('ascii'))
                client.close()
                continue


        usernames.append(username)  
        clients.append(client)

        now = time.localtime()
        current_time = time.strftime("%H:%M" , now)

        print(f"[{current_time}]:{username} has joined.")
        distributer(f"{username} joined the chat.".encode('ascii'))
        client.send("Connected to the server.".encode('ascii'))
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

#-------------------------------------distributing messages to clients----------------------------------------



def distributer(message):
    for client in clients:
        client.send(message)


#------------------------------------checking the password-----------------------------------------

def check_password(password_entered):
        password = b"anything"
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        password1 = password_entered.encode('utf-8')
        if bcrypt.checkpw(password1, hashed):
            return False
        else:
            return True


#--------------------------------handling messages before distributing them---------------------------------------------

def handle(client):
    while True:
        try:
            checker = message = client.recv(1024)
            if checker.decode('ascii').startswith('KICK'):

                if usernames[clients.index(client)] == 'admin':
                    user_kicked = checker.decode('ascii')[5:]
                    kick_user(user_kicked)
                else:
                    client.send("Command was refused!".encode('ascii'))

            elif checker.decode('ascii').startswith('BAN'):

                if usernames[clients.index(client)] == 'admin':
                    name_to_ban = checker.decode('ascii')[4:]
                    kick_user(name_to_ban)

                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f"{name_to_ban} was banned!")
                    
                else:
                    client.send("Command was refused!".encode('ascii'))
            else:
                distributer(message)

        except:
            if client in clients:
                index = clients.index(client)       
                clients.remove(client)   
                client.close()
                username = usernames[index]
                distributer(f"{username} has left the chat.".encode('ascii'))
                usernames.remove(username)
                break

#--------------------------------kicking users---------------------------------------------

def kick_user(name):
    if name in usernames:

        name_index = usernames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You were kicked from the server!".encode('ascii'))
        client_to_kick.close()
        usernames.remove(name)
        distributer(f'{name} was kicked from the server.'.encode('ascii'))
        print(f"{name} was kicked.")

#-----------------------------------------------------------------------------

print("server initiated.")
connecter()
