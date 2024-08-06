import socket
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
import os
import hashlib
from encryption_library import *

#parent class for all the different screens
#it allows the user to switch between screens
class page(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        self.configure(background = BG) #sets the background colour

    def go_to(self, page):
        page.pack(padx=10, pady=10)
        self.pack_forget()

    def find_ip(self, name): #searches contact list for an ip address
        try:
            file = open("contacts.txt","r")
        except:
            print("no existing contacts")
            return 0
        
        contents = file.read()
        if "," not in contents:
            print("no existing contacts")
            return 0

        for line in contents.split("\n"): #iterates through each line of the contact lis
            data = line.split(",")
            if len(data) != 2:
                return -1
            username = data[0]
            ip = data[1]
            
            if username == name:
                return ip
            
        file.close()
        
        return -1 #-1 shows that the given name is not in the contact list

    def check_keys(self, N, E, D): #checks if a set of encryption keys is valid
        
        if N == "" or E == "" or D == "": #checks if the keys are empty
            self.go_to(new_keys(self))
            return -1
        else:
            try:
                if int(N) < 0 or int(E) < 0 or int(D) < 0: #checks if the keys are positive integers
                    self.go_to(new_keys(self))
                    return -1
                else:
                    if transform(transform("encryption test",(int(N),int(E))),(int(N),int(D))) == "encryption test": #checks if the keys work properly
                        public_key = (int(N),int(E))
                        private_key = (int(N),int(D))
                    else:
                        self.go_to(new_keys(self))
                        return -1
            except:
                self.go_to(new_keys(self))
                return -1
        
        return (public_key, private_key)

#join chat screen
class join_chat(page):
    def __init__(self):
        page.__init__(self)
        
        title = tk.Label(self, text = "join chat\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 1)

        prompt1 = tk.Label(self, text = "enter chat host:", bg = BG, fg = FG)
        prompt1.grid(row = 1, column = 0, sticky = "W")

        #will take the IP address of the contact as a required input in the future
        host = tk.Entry(self, width = 30, bg = BG2, fg = FG)
        host.grid(row = 2, column = 0, columnspan = 2, sticky = "W")

        note1 = tk.Label(self, text = "(required field)", bg = BG, fg = FG)
        note1.grid(row = 2, column = 2, columnspan = 2)

        prompt2 = tk.Label(self, text = "enter public key:", bg = BG, fg = FG)
        prompt2.grid(row = 3, column = 0, sticky = "W")

        n = tk.Label(self, text = "N:", bg = BG, fg = FG)
        n.grid(row = 4, column = 0, sticky = "W")

        e = tk.Label(self, text = "E:", bg = BG, fg = FG)
        e.grid(row = 4, column = 1, sticky = "W")

        d = tk.Label(self, text = "D:", bg = BG, fg = FG)
        d.grid(row = 4, column = 2, sticky = "W")

        #will take the public key exponent 'N' as a required input in the future
        self.N = tk.Entry(self, width = 10, bg = BG2, fg = FG)
        self.N.grid(row = 5, column = 0, sticky = "W")

        #takes the public key exponent 'E' as an input
        self.E = tk.Entry (self, width = 10, bg = BG2, fg = FG)
        self.E.grid(row = 5, column = 1, sticky = "W")

        #will take the public key exponent 'D' as a required input in the future
        self.D = tk.Entry(self, width = 10, bg = BG2, fg = FG)
        self.D.grid(row = 5, column = 2, sticky = "W")

        note2 = tk.Label(self, text = "(leave blank to generate new keys\nenter all zeros to skip encryption)", bg = BG, fg = FG)
        note2.grid(row = 5, column = 3, columnspan = 2)

        #takes the user to the chat screen
        enter = tk.Button(self, text = "enter", command = lambda : self.verify_key(host.get(), self.N.get(), self.E.get(), self.D.get()), bg = BG, fg = FG)
        enter.grid(row = 6, column = 0, sticky = "W")

        #goes back to the menu when pressed
        back = tk.Button(self, text = "back", command = lambda : self.go_to(menu()), bg = BG, fg = FG)
        back.grid(row = 6, column = 1)

        refresh = tk.Button(self, text = "refresh keys", command = lambda : self.refresh_keys(), bg = BG, fg = FG)
        refresh.grid(row = 6, column = 2, sticky = "E")
        
        self.refresh_keys()

    def refresh_keys(self):
        self.N.delete(0, tk.END)
        self.E.delete(0, tk.END)
        self.D.delete(0, tk.END)
        
        self.N.insert(0, str(PUBLIC_KEY[0]))
        self.E.insert(0, str(PUBLIC_KEY[1]))
        self.D.insert(0, str(PRIVATE_KEY[1]))

    def verify_key(self, contact_name, N, E, D): #verifiys if keys have been generated or not
        
        keys = self.check_keys(N, E, D)
        if keys == -1:
            return
        else:
            public_key = keys[0]
            private_key = keys[1]
            self.connect_host(contact_name, public_key, private_key)
    
    def connect_host(self, contact_name, public_key, private_key): #connects to the user hosting the chat session
                
        address = self.find_ip(contact_name)
        
        if address == -1 or address == 0: #exits if no contact information was found
            print("contact not found")
            messagebox.showerror(title = "error", message = "contact not found")
            return
        
        SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates a socket which will allow data to be sent and received
        SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #sets the socket to be reusable
        SOCKET.bind((SELF_IP, SELF_PORT)) #assigns the user's IP address and port to the socket
        
        try:
            SOCKET.connect((address, REMOTE_PORT))
        except:
            print("host did not respond")
            return

        key_transfer = bytes(str(public_key[0])+","+str(public_key[1]), FORMAT)
        SOCKET.send(key_transfer)
        public_key = SOCKET.recv(BUFFER_SIZE)
        public_key = public_key.decode(FORMAT)
        public_key = public_key.split(",")
        public_key = (int(public_key[0]), int(public_key[1]))
        
        self.go_to(chat(self, SOCKET, (address, REMOTE_PORT), contact_name, public_key, private_key))
        


#host chat screen
class host_chat(page):
    def __init__(self):
        page.__init__(self)
        
        title = tk.Label(self, text = "host chat\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 1)

        prompt1 = tk.Label(self, text = "enter chat recipient:", bg = BG, fg = FG)
        prompt1.grid(row = 1, column = 0, sticky = "W")

        #will take the IP address of the contact as a required input in the future
        recipient = tk.Entry(self, width = 30, bg = BG2, fg = FG)
        recipient.grid(row = 2, column = 0, columnspan = 2, sticky = "W")

        note1 = tk.Label(self, text = "(required field)", bg = BG, fg = FG)
        note1.grid(row = 2, column = 2, columnspan = 2)

        prompt2 = tk.Label(self, text = "enter public key:", bg = BG, fg = FG)
        prompt2.grid(row = 3, column = 0, sticky = "W")

        n = tk.Label(self, text = "N:", bg = BG, fg = FG)
        n.grid(row = 4, column = 0, sticky = "W")

        e = tk.Label(self, text = "E:", bg = BG, fg = FG)
        e.grid(row = 4, column = 1, sticky = "W")

        d = tk.Label(self, text = "D:", bg = BG, fg = FG)
        d.grid(row = 4, column = 2, sticky = "W")

        #takes the common key exponent 'N' as an input
        self.N = tk.Entry(self, width = 10, bg = BG2, fg = FG)
        self.N.grid(row = 5, column = 0, sticky = "W")

        #takes the public key exponent 'E' as an input
        self.E = tk.Entry (self, width = 10, bg = BG2, fg = FG)
        self.E.grid(row = 5, column = 1, sticky = "W")

        #takes the public key exponent 'D' as an input
        self.D = tk.Entry(self, width = 10, bg = BG2, fg = FG)
        self.D.grid(row = 5, column = 2, sticky = "W")

        note2 = tk.Label(self, text = "(leave blank to generate new keys\nenter all zeros to skip encryption)", bg = BG, fg = FG)
        note2.grid(row = 5, column = 3, columnspan = 2)

        #takes the user to the chat screen
        enter = tk.Button(self, text = "enter", command = lambda : self.verify_key(recipient.get(), self.N.get(), self.E.get(), self.D.get()), bg = BG, fg = FG)
        enter.grid(row = 6, column = 0, sticky = "W")

        #goes back to the menu when pressed
        back = tk.Button(self, text = "back", command = lambda : self.go_to(menu()), bg = BG, fg = FG)
        back.grid(row = 6, column = 1)

        refresh = tk.Button(self, text = "refresh keys", command = lambda : self.refresh_keys(), bg = BG, fg = FG)
        refresh.grid(row = 6, column = 2, sticky = "E")

        self.refresh_keys()

    def refresh_keys(self):
        self.N.delete(0, tk.END)
        self.E.delete(0, tk.END)
        self.D.delete(0, tk.END)
        
        self.N.insert(0, str(PUBLIC_KEY[0]))
        self.E.insert(0, str(PUBLIC_KEY[1]))
        self.D.insert(0, str(PRIVATE_KEY[1]))
    
    def verify_key(self, contact_name, N, E, D): #verifiys if keys have been generated or not
        
        keys = self.check_keys(N, E, D)
        if keys == -1:
            return
        else:
            public_key = keys[0]
            private_key = keys[1]
            self.start_listen(contact_name, public_key, private_key)
    
    def start_listen(self, contact_name, public_key, private_key): #allows the intended recipient to connect to the chat session
        
        contact_address = self.find_ip(contact_name)

        if contact_address == -1 or contact_address == 0: #exits if no contact information was found
            print("contact not found")
            messagebox.showerror(title = "error", message = "contact not found")
            return
        
        SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates a socket which will allow data to be sent and received
        SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #sets the socket to be reusable
        SOCKET.bind((SELF_IP, SELF_PORT)) #assigns the user's IP address and port to the socket
        
        address = ("", 0)
        SOCKET.listen() #the program waits for an incoming connection
        while address[0] != contact_address:
            connection, address = SOCKET.accept() #the connection and the socket address (IP address, port) is stored
            if address[0] != contact_address:
                connection.close() #closes the connection if it is not the intended recipient

        key_transfer = bytes(str(public_key[0])+","+str(public_key[1]), FORMAT)
        connection.send(key_transfer)
        public_key = connection.recv(BUFFER_SIZE)
        public_key = public_key.decode(FORMAT)
        public_key = public_key.split(",")
        public_key = (int(public_key[0]), int(public_key[1]))
        self.go_to(chat(self, connection, address, contact_name, public_key, private_key)) #takes the user to the chat screen and passes the connection and socket address over as parameters



#chat screen
class chat(page):
    def __init__(self, previous, connection, address, username, public_key, private_key):
        page.__init__(self)

        self.public = public_key
        self.private = private_key

        self.previous = previous #stores the previous screen so the user can return to it
        self.username = username
        
        title = tk.Label(self, text = "chat\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 1)

        #displays both sent and received messages
        self.log = tk.Text(self, width = 50, bg = BG2, fg = FG)
        self.log.grid(row = 1, column = 0, columnspan = 3)

        prompt = tk.Label(self, text = "enter message:", bg = BG, fg = FG)
        prompt.grid(row = 2, column = 0, sticky = "W")

        #takes the a message form the user as an input
        self.message = tk.Entry(self, width = 40, bg = BG2, fg = FG)
        self.message.grid(row = 3, column = 0, columnspan = 2, sticky = "W")

        #sends the message input by the user
        send = tk.Button(self, text = "send", command = lambda : self.send_message(connection, address, self.message.get()), bg = BG, fg = FG)
        send.grid(row = 3, column = 2, sticky = "E")

        #takes the user back to the previous screen (either the host chat screen or the join chat screen)
        back = tk.Button(self, text = "back", command = lambda : self.exit_chat(connection), bg = BG, fg = FG)
        back.grid(row = 4, column = 2, sticky = "E")

        self.thread = threading.Thread(target = self.update_chat, args = (connection, address))
        self.thread.start() #runs update_chat in the background so users can send and receive messages simultaneously

        app.bind("<Return>", lambda event:self.send_message(connection, address, self.message.get())) #allows the user to send a message by pressing the enter key

    def update_chat(self, conn, addr): #displays any recieved messages in the self.log
        while True:
            try:
                msg = conn.recv(BUFFER_SIZE) #receives message as binary data
            except:
                return

            msg = msg.decode(FORMAT) #converts binary message to utf-8
            msg = transform(msg, self.private) #decrypts message
            self.log.insert(tk.END, self.username+": "+msg+"\n")
            self.log.update_idletasks()
            self.log.see("end")

            if msg == "CONNECTION CLOSED": #breaks the loop when the other user disconnects
                messagebox.showinfo(title = "connection closed", message = "other user disconnected")
                return

    def send_message(self, conn, addr, msg): #sends message in binary format and adds it to self.log
        if len(msg) > BUFFER_SIZE or len(msg) < 1:
            return
        
        original_msg = msg
        msg = transform(msg, self.public) #encrypts message
        msg = bytes(msg, FORMAT) #converts message to binary
        try:
            conn.send(msg)
        except:
            print("message did not send, connection may be closed")
        self.log.insert(tk.END, "you: "+original_msg+"\n") #displays message
        self.log.see("end")
        self.message.delete(0, "end")

    def exit_chat(self, conn):
        msg = bytes(transform("CONNECTION CLOSED", self.public), FORMAT)
        try:
            conn.send(msg)
        except:
            print("connection already closed")
        conn.shutdown(socket.SHUT_RDWR) #resets the socket so that all connections can be closed
        conn.close() #closes connection
        self.go_to(self.previous) #takes the user back to the join/host chat screen


#generate new keys screen
class new_keys(page):
    def __init__(self, previous):
        page.__init__(self)

        self.previous = previous
        
        #components needed to create keys
        self.key_N = 0
        self.key_E = 0
        self.key_D = 0
        self.key_X = 0
        self.key_Y = 0
        self.key_TOTIENT = 0
        
        title = tk.Label(self, text = "generate new keys\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 0, columnspan = 4)

        prompt1 = tk.Label(self, text = "X:", bg = BG, fg = FG)
        prompt1.grid(row = 1, column = 0, sticky = "W")

        prompt2 = tk.Label(self, text = "Y:", bg = BG, fg = FG)
        prompt2.grid(row = 1, column = 1, sticky = "W")

        x = tk.Entry(self, width = 20, bg = BG2, fg = FG)
        x.grid(row = 2, column = 0)

        y = tk.Entry(self, width = 20, bg = BG2, fg = FG)
        y.grid(row = 2, column = 1)

        info1 = tk.Button(self, text = "i", command = lambda : self.show_info("x and y are prime numbers that are used to create encryption keys."), bg = BG, fg = FG)
        info1.grid(row = 2, column = 2)

        enter1 = tk.Button(self, text = "enter", command = lambda : self.calculate_N(x.get(), y.get()), bg = BG, fg = FG)
        enter1.grid(row = 2, column = 3)

        prompt3 = tk.Label(self, text = "N:", bg = BG, fg = FG)
        prompt3.grid(row = 3, column = 0, sticky = "W")

        self.N = tk.StringVar(self, "  x*y  ")
        
        self.n = tk.Label(self, textvariable = self.N, bg = BG2, fg = FG)
        self.n.grid(row = 4, column = 0, sticky = "W")

        info2 = tk.Button(self, text = "i", command = lambda : self.show_info("N is the component that is used in both keys. it is calculated by multiplying x and y."), bg = BG, fg = FG)
        info2.grid(row = 4, column = 1, sticky = "W")

        prompt4 = tk.Label(self, text = "E:", bg = BG, fg = FG)
        prompt4.grid(row = 5, column = 0, sticky = "W")

        prompt5 = tk.Label(self, text = "D:", bg = BG, fg = FG)
        prompt5.grid(row = 5, column = 3)

        self.selected = tk.StringVar(self, "choose a value")
        self.options = ["empty"]
        
        self.e = tk.OptionMenu(self, self.selected, *self.options)
        self.e.config(bg = BG, fg = FG)
        self.e["menu"].config(bg = BG2, fg = FG)
        self.e.grid(row = 6, column = 0)

        info3 = tk.Button(self, text = "i", command = lambda : self.show_info("E is the public key component. it is calculated by finding a coprime of the totient of N that is between 1 and the totient. the totient is calculated by multiplying x-1 and y-1."), bg = BG, fg = FG)
        info3.grid(row = 6, column = 1, sticky = "W")

        enter2 = tk.Button(self, text = "enter", command = lambda : self.calculate_D(), bg = BG, fg = FG)
        enter2.grid(row = 6, column = 2)

        self.D = tk.StringVar(self, "          ")
        
        self.d = tk.Label(self, textvariable = self.D, bg = BG2, fg = FG)
        self.d.grid(row = 6, column = 3)

        info4 = tk.Button(self, text = "i", command = lambda : self.show_info("D is the private key component. it is calculated by finding the positive coefficient that satisfys bezout's identity with E and the totient of N. this is when A*totient + B*E = highest common factor of the totient and E. D is the positive coefficient out of A and B."), bg = BG, fg = FG)
        info4.grid(row = 6, column = 4, sticky = "W")

        prompt6 = tk.Label(self, text = "public: ", bg = BG, fg = FG)
        prompt6.grid(row = 7, column = 0, sticky = "E")

        self.public = tk.StringVar(self, "  (N,E)  ")

        self.public_key = tk.Label(self, textvariable = self.public, bg = BG2, fg = FG)
        self.public_key.grid(row = 7, column = 1, sticky = "W")

        prompt6 = tk.Label(self, text = "private: ", bg = BG, fg = FG)
        prompt6.grid(row = 7, column = 2, sticky = "E")

        self.private = tk.StringVar(self, "  (N,D)  ")

        self.private_key = tk.Label(self, textvariable = self.private, bg = BG2, fg = FG)
        self.private_key.grid(row = 7, column = 3, sticky = "W")

        use = tk.Button(self, text = "use key",command = lambda : self.use_key(), bg = BG, fg = FG)
        use.grid(row = 8, column = 0)

        back = tk.Button(self, text = "back", command = lambda : self.go_to(previous), bg = BG, fg = FG)
        back.grid(row = 8, column = 1)

    def calculate_N(self, x, y): #calculates and displays new value of N
        try:
            x = int(x)
            y = int(y)
        except:
            messagebox.showwarning(title = "warning", message = "x and y must be prime numbers")
            return
        
        if is_prime(x) == False or is_prime(y) == False:
            messagebox.showwarning(title = "warning", message = "x and y must be prime numbers")
            return

        self.key_X = x
        self.key_Y = y
        
        N = x*y
        self.key_N = N
        self.N.set(str(N))
        self.n.update_idletasks()

        self.calculate_E()

    def calculate_E(self): #calculates all possible E values and adds them to the options menu
        self.public.set("  (N,E)  ")
        self.private.set("  (N,D)  ")
        self.D.set("          ")
        if self.key_N == 0:
            return

        self.key_TOTIENT = totient(self.key_X, self.key_Y)
        E_values = coprimes(self.key_TOTIENT)

        if len(E_values) == 0:
            return
        
        self.options = E_values
        self.selected.set("choose a value")
        self.e["menu"].delete(0, "end")
        for i in E_values:
            option = str(i)
            self.e["menu"].add_command(label = option, command = tk._setit(self.selected, option))

    def calculate_D(self): #calculates the value of D
        try:
            self.key_E = int(self.selected.get())
        except:
            messagebox.showwarning(title = "warning", message = "E value not selected")
            return

        self.public.set("( " + str(self.key_N) + " , " + str(self.key_E) + " )")

        self.key_D = D(self.key_TOTIENT, self.key_E, self.key_N)
        
        self.D.set(str(self.key_D))
        self.private.set("( " + str(self.key_N) + " , " + str(self.key_D) + " )")

    def use_key(self): #checks if a working encryption key has been generated
        global PUBLIC_KEY
        global PRIVATE_KEY
        
        if self.key_N == 0 or self.key_E == 0 or self.key_D == 0:
            return
        
        if transform(transform("encryption test", (self.key_N, self.key_E)), (self.key_N, self.key_D)) != "encryption test":
            messagebox.showerror(title = "error", message = "encryption keys did not work. try choosing a higher value for E or higher prime numbers for x and y")
            return

        PUBLIC_KEY = [self.key_N, self.key_E]
        PRIVATE_KEY = [self.key_N, self.key_D]

        self.go_to(self.previous)

    def show_info(self, info):
        messagebox.showinfo(title = "info", message = info)


#new contact screen
class new_contact(page):
    def __init__(self):
        page.__init__(self)
        
        title = tk.Label(self, text = "new contact\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 0, columnspan = 3)

        prompt1 = tk.Label(self, text = "name:", bg = BG, fg = FG)
        prompt1.grid(row = 1, column = 0, sticky = "W")

        #takes the name of the new contact as an input
        name = tk.Entry(self, width = 50, bg = BG2, fg = FG)
        name.grid(row = 2, column = 0, columnspan = 3)

        prompt2 = tk.Label(self, text = "IP address:", bg = BG, fg = FG)
        prompt2.grid(row = 3, column = 0, sticky = "W")

        #takes the IP address of the new contact as an input
        address = tk.Entry(self, width = 50, bg = BG2, fg = FG)
        address.grid(row = 4, column = 0, columnspan = 3)

        #will add the new contact to the contact list file in the future
        save = tk.Button(self, text = "save", command = lambda : self.add_contact(name.get(), address.get()), bg = BG, fg = FG)
        save.grid(row = 5, column = 0, sticky = "W")

        #takes the user back to the menu
        back = tk.Button(self, text = "back", command = lambda : self.go_to(menu()), bg = BG, fg = FG)
        back.grid(row = 5, column = 2, sticky = "E")

    def add_contact(self, name, IP):
        if name == "" or len(name) > 25 or "\n" in name or "\\n" in name or "," in name: #checks if the name is valid
            messagebox.showwarning(title = "warning", message = "username must be between 1 and 25 characters and it must not contain commas or newline characters")
            return
        if IP == "" or "," in IP or "\n" in IP or "\\n" in IP or "." not in IP: #checks if the IP address is valid
            messagebox.showwarning(title = "warning", message = "IP address must not be empty, it must not contain commas or newline characters and it must contain 3 full stops")
            return
        else:
            ip = IP.split(".")
            if len(ip) != 4: #checks if the IP has only 4 sections
                messagebox.showwarning(title = "warning", message = "IP address must have 4 numbers separated by full stops")
                return
            else:
                for i in ip:
                    try: #checks if the ip address is made up of integer values
                        if int(i) < 0 or int(i) > 255: #checks if integer values are within the possible range
                            messagebox.showwarning(title = "warning", message = "IP address must not contain numbers below 0 or above 255")
                            return
                    except:
                        messagebox.showwarning(title = "warning", message = "IP address must contain only numbers and full stops")
                        return

        exists = self.find_ip(name) #checks if the username is already in use
        if exists != -1 and exists != 0:
            print("username already in use")
            messagebox.showwarning(title = "warning", message = "username already in use")
            return
        
        try:
            file = open("contacts.txt", "x") #creates new contact list file if one is needed
            file.close()
            file = open("contacts.txt","w")
            file.write("SELF," + SELF_IP)
            file.close()
        except:
            print("contact list file found")

        file = open("contacts.txt", "a")
        file.write(name+","+IP+"\n") #adds new contact to contact list file
        file.close()
        print("contact added")
        messagebox.showinfo(title = "success", message = "contact added successfully")
            


#contact list screen
class contact_list(page):
    def __init__(self):
        page.__init__(self)

        title = tk.Label(self, text = "contact list\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 0, columnspan = 3)

        #will display the contents of the contact list in the future
        self.contacts = tk.Text(self, width = 50, bg = BG2, fg = FG)
        self.contacts.grid(row = 1, column = 0, columnspan = 3)

        #will save any changes made to the contact list in the future
        save = tk.Button(self, text = "save changes", command = lambda : self.save_list(self.contacts.get("1.0",tk.END)), bg = BG, fg = FG)
        save.grid(row = 2, column = 0, sticky = "W")

        #takes the user back to the menu
        back = tk.Button(self, text = "close", command = lambda : self.go_to(menu()), bg = BG, fg = FG)
        back.grid(row = 2, column = 2, sticky = "E")

        #outputs all existing contacts to the GUI
        try:
            file = open("contacts.txt", "r")
            for line in file:
                self.contacts.insert(tk.END, line)
                self.contacts.update_idletasks()
                self.contacts.see("end")
            file.close()
        except:
            file = open("contacts.txt","x")
            file.close()
            file = open("contacts.txt","w")
            file.write("SELF," + SELF_IP)
            file.close()
            self.contacts.insert(tk.END, "SELF," + SELF_IP + "\n")

    def save_list(self, contacts): #saves changes made by the user to the contact list
        contacts = contacts.split("\n")
        unusable = []
        usernames = []
        
        for i in contacts: #marks all lines with invalid data to be removed
            if i == "" or i == "NO EXISTING CONTACTS":
                unusable.append(i)
            elif len(i.split(",")) != 2:
                unusable.append(i)
            else:
                data = i.split(",")
                name = data[0]
                IP = data[1]
                
                if name == "" or len(name) > 25 or "\n" in name or "\\n" in name or name in usernames: #checks if the name is valid and not already in use
                    unusable.append(i)
                elif IP == "" or "\n" in IP or "\\n" in IP or "." not in IP: #checks if the IP address is valid
                    unusable.append(i)
                else:
                    ip = IP.split(".")
                    if len(ip) != 4: #checks if the IP has only 4 sections
                        unusable.append(i)
                    else:
                        for j in ip:
                            try: #checks if the ip address is made up of integer values
                                if int(j) < 0 or int(j) > 255: #checks if integer values are within the possible range
                                    unusable.append(i)
                            except:
                                unusable.append(i)
                                
                if name not in usernames and i not in unusable:
                    usernames.append(name)
                
        for i in unusable: #removes all unusable lines
            try:
                contacts.remove(i)
            except:
                print("line already removed")

        contacts = "\n".join(contacts) + "\n"
        
        file = open("contacts.txt","w")
        file.write(contacts) #saves changes to contact list file
        file.close()

        self.contacts.delete("1.0", tk.END) #displays new contact list with all invalid data removed
        self.contacts.insert(tk.END, contacts)
        self.contacts.update_idletasks()
        messagebox.showinfo(title = "success", message = "contact info saved")


#new password screen
class new_password(page):
    def __init__(self):
        page.__init__(self)

        title = tk.Label(self, text = "new password\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 0, columnspan = 3)

        #takes the new password as an input
        password = tk.Entry(self, width = 50, show = "*", bg = BG2, fg = FG)
        password.grid(row = 1, column = 0, columnspan = 3)

        #will save the new password to a file in the future
        save = tk.Button(self, text = "save", command = lambda : self.set_password(password.get()), bg = BG, fg = FG)
        save.grid(row = 2, column = 0, sticky = "W")

        #takes the user back to the menu
        back = tk.Button(self, text = "back", command = lambda : self.go_to(menu()), bg = BG, fg = FG)
        back.grid(row = 2, column = 2, sticky = "E")

    def set_password(self, new): #hashes and saves new password
        if new == "":
            try:
                os.remove("password.txt") #deletes password file if the user is removing their password
                messagebox.showinfo(title = "success", message = "password removed")
            except:
                print("no password to remove")
                messagebox.showinfo(title = "success", message = "password removed")
        else:
            try:
                file = open("password.txt", "x") #creates new password file if one is needed
                file.close()
            except:
                print("password file found")
            file = open("password.txt", "w")
            file.write(hashlib.sha256(new.encode()).hexdigest()) #hashes and stores new password in password file
            file.close()
            messagebox.showinfo(title = "success", message = "password successfully changed")
            


#menu screen
class menu(page):
    def __init__(self):
        page.__init__(self)
        
        title = tk.Label(self, text = "menu\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 0, columnspan = 3)

        #will take the user to the host chat screen when pressed
        host = tk.Button(self, text = "host chat", command = lambda : self.go_to(host_chat()), bg = BG, fg = FG)
        host.grid(row = 1, column = 0, sticky = "W")

        #will take the user to the join chat screen when pressed
        join = tk.Button(self, text = "join chat", command = lambda : self.go_to(join_chat()), bg = BG, fg = FG)
        join.grid(row = 1, column = 1, sticky = "W")

        #will close the app when pressed
        quitbutton = tk.Button(self, text = "quit", command = lambda : quit(), bg = BG, fg = FG)
        quitbutton.grid(row = 1, column = 2, sticky = "W")

        #will take the user to the new contact screen when pressed
        newcontact = tk.Button(self, text = "new contact", command = lambda : self.go_to(new_contact()), bg = BG, fg = FG)
        newcontact.grid(row = 2, column = 0, sticky = "W")

        #will take the user to the contact list screen when pressed
        contactlist = tk.Button(self, text = "contact list", command = lambda : self.go_to(contact_list()), bg = BG, fg = FG)
        contactlist.grid(row = 2, column = 1, sticky = "W")

        #will take the user to the new password screen when pressed
        newpassword = tk.Button(self, text = "new password", command = lambda : self.go_to(new_password()), bg = BG, fg = FG)
        newpassword.grid(row = 3, column = 0, sticky = "W")


#password screen
class password(page):
    def __init__(self, password_hash):
        page.__init__(self)

        title = tk.Label(self, text = "enter password\n", bg = BG, fg = FG)
        title.grid(row = 0, column = 0, columnspan = 3)

        #takes the password as an input
        passwordbox = tk.Entry(self, width = 50, show = "*", bg = BG2, fg = FG)
        passwordbox.grid(row = 1, column = 0, columnspan = 3)

        #will take the user to the menu if the password entered is correct
        enter = tk.Button(self, text = "enter", command = lambda : self.check_password(password_hash, passwordbox.get()), bg = BG, fg = FG)
        enter.grid(row = 2, column = 0, columnspan = 3)

    def check_password(self, stored_hash, input_password): #checks if the password is correct
        if stored_hash == hashlib.sha256(input_password.encode()).hexdigest():
            self.go_to(menu())
        else:
            messagebox.showerror(title = "incorrect", message = "incorrect password")


#class for the actual app window
class APP(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.configure(background = BG) #sets the background colour
        self.resizable(False,False) #stops the user from resizing the window
        self.title("secure messaging app")

        try:
            file = open("password.txt", "r")
            PASSWORD = file.readline()
            file.close()
            #adds the password screen to the app window if a password exists
            if PASSWORD != "":
                password(PASSWORD).pack(padx=10, pady=10)
        except:
            print("no password set")
            #adds the menu screen to the app window if no password exists
            menu().pack(padx=10, pady=10)
        

#GLOBAL VARIABLES
SELF_IP = socket.gethostbyname(socket.gethostname()) #IP address of the user's device
SELF_PORT = 5054 #port number on the user's computer that the program will use to send and receive data
REMOTE_PORT = 5050 #port number on the recipients computer that the program will use to send and receive data
BUFFER_SIZE = 1024 #the amount of data received at any given time
FORMAT = "utf-8" #the format that data is converted to/from binary
BG = "#25344d" #background colour
BG2 = "#5d6f8c" #background colour
FG = "white" #foreground colour
PUBLIC_KEY = [0,0]
PRIVATE_KEY = [0,0]

#runs the app
app = APP()
app.mainloop()
