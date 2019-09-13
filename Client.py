import socket
import logging
import time

#-------------------------------------------------- CONFIGURE LOGGING FORMAT --------------------------------------------------->
logging.basicConfig(filename='Client.log', level=logging.INFO, format='%(asctime)s:  %(message)s', datefmt="%H:%M:%S on %d-%m-%Y")
#<------------------------------------------------------------------------------------------------------------------------------>


#<- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >
#<----------------------- SETUP THE CLIENT SOCKET ----------------------->
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                    #create a socket, sock stream lets us make it a tcp connection
connectedToServer = False                                                           #sets variable connectedToServer to false initially
try:
    clientSocket.connect(('127.0.0.1', 4242))                                       #connect to port 4242
    connectedToServer = True                                                        #now connected to server
    print('Connection to server was successful'+'\n')                               #print to the terminal that the connection was successful
except ConnectionRefusedError:                                                      #catch a connectionRefusedError - occurs when client is refused connection to the server
    print("Server is unavailable / not running")                                    #print to terminal that the server is refusing the connection
except OSError:                                                                     #catch an OS error
    print('Connection to server was unsuccessful - port 4242 is busy'+'\n')         #print to terminal that the port is busy
#<----------------------------------------------------------------------->

while connectedToServer:                                                                    #while the client is connected to server
    #<----------------- RECEIVE AND CLEAN VALID USER INPUT ------------------>
    try:
        validInput = False                                                                  #initially, valid input is false
        while not validInput:                                                               #while the input is not valid
            inputString = input('Input artist name or "quit" to disconnect: ')              #receive input
            inputString = inputString.strip('"'"'"' ').upper()                              #removes leading and trailing whitespace and commas, converts to uppercase (all artists in song bank are stored in upper case)           
            while '  ' in inputString:                                                      #while there are double whitespaces within artist name
                inputString = inputString.replace('  ',' ')                                 #replace them with a single whitespace
            if inputString != "":                                                           #if the input is not empty after string is cleaned, this is considered valid
                validInput = True                                                           #input is considered valid
            else:                                                                           #otherwise
                print('Empty input is not valid - input alphanumeric characters')           #print to console that the input is not valid
                #<----------------------------------------------------------------------->


        #<----------------- SEND THE INPUT AND CHECK FOR RECEIPT ---------------->
        received = False                                                                #received is initially false
        while not received:                                                             #while received is false
            clientSocket.send(inputString.encode())                                     #send the input to server
            sendTime = time.time()                                                      #capture the time of sending input
            serverRecv = clientSocket.recv(1024).decode()                               #receive the servers response (SUCCESS OR FAILURE)
            if serverRecv == 'SUCCESS':                                                 #if response is a success
                received = True                                                         #set received to true
        #<----------------------------------------------------------------------->

        #<-------------- RECEIVE SONG LIST FROM SERVER AND PRINT ----------------> 
        bytesRecv = clientSocket.recv(1024)                                                                         #receive the response from the server - need to keep this so that we can calculate the length of the response in bytes
        string = bytesRecv.decode()                                                                                 #decode response from the server, an artist or an error

        if string == "":                                                                                            #if nothing is received - this indicates that the server closed the connection in response to a "quit" command                          
            raise ConnectionResetError                                                                              #otherwise, consider that an artist was received
        else:
            if string == 'KeyError':                                                                                #if the string is a keyerror, then the artist does not exist
                print('Artist "'+inputString.title()+'" does not exist'+'\n')                                       #print to terminal that the artist does not exist
            else:
                logging.info('Server response received at '+time.strftime("%H:%M:%S")+                              #Write to log the time that the servers response was received at a given time
                 ' on '+time.strftime("%d/%m/%Y")+'\r\n')                                           
                logging.info('Time taken for server to respond to request for songs by '+                           #write to log file the time taken for server to respond
                             inputString.title()+' : '+str((time.time()-sendTime)*1000)+' ms'+'\r\n')
                logging.info('The response length was '+str(len(bytesRecv))+' bytes'+'\r\n\r\n')                    #write server response length to log file
                print('\n'+'The following songs are associated with artist '+ inputString.title()+'\r\n')           #print to the terminal the name of the artist whos songs were retrieved
                string = string[1:-1]                                                                               #removes the square brackets [] from the string representing a list of songs e.g. ['song1','song2']
                songList = string.split(',')                                                                        #form a song list - split the string around commas (they separate song titles)
                for songNo, song in enumerate(songList,1):                                                          #for each song in the list of songs
                    song = song.strip('"'"'"' ')                                                                    #strip spaces and quotation marks from the string
                    print('Song '+str(songNo)+': '+song+'\n')                                                       #print the song number and song title to terminal
        #<----------------------------------------------------------------------->
    except (ConnectionResetError, BrokenPipeError):                                                                 #catch a connection reset error and broken pipe error - both of which indicate that the connection should close
        clientSocket.close()                                                                                        #close the client socket
        print("Server disconnected from client - connection closed")                                                #print to terminal that the connection is closed
        connectedToServer = False                                                                                   #set variable connected to server to false to exit the while loop
#<- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >

