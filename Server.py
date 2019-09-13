import socket
import logging
import time

#-------------------------------------------------- CONFIGURE LOGGING FORMAT --------------------------------------------------->
logging.basicConfig(filename='Server.log', level=logging.INFO, format='%(asctime)s:  %(message)s', datefmt="%H:%M:%S on %d-%m-%Y")
#<------------------------------------------------------------------------------------------------------------------------------>


#<- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >
#<--------------- READ THE TEXT FILE INTO A DICTIONARY -------------->
with open('100worst.txt') as textFile:
    songBank = {}                                                           #initialise variable songBank as an empty dictionary
    for lineNo, line in enumerate(textFile):                                #iterate through each line in the text file individually
        line = line[4:]                                                     #remove the first 4 characters from line
        if lineNo > 5 and lineNo < 112:                                     #only want to apply the following block of code to lines contaianing song names or artists
            line = line.rstrip('\n'); line = line.lstrip()                  #removes new line characters and leading whitespace
            index = line.find('  ')                                         #look for the first occurence of a double space
            if index == -1 and not line.isdigit():                          #if there are no occurences of a double space and the line consists of more than just the year
                song = line[:]                                              #this indicates that our line is a song title on a line of its own
            else:                                                           #otherwise, there is more information to be extracted from the line
                restOfLine = line[index:].lstrip()                          #assign the portion of the line after the double space to variable restOfLine
                if restOfLine.isdigit():                                    #if this section of the line is a year (e.g. 1974), we know that our line currently represents an artist
                    artist = line[:index].upper()                           #assign the string corresponding to the artist name to the variable artist - converting to uppercase so that we can compare against this string easily later
                else:                                                       #otherwise, the remaining portion of the line has more than just a year, therefore must also include the song too
                    song = line[:index]                                     #first portion of the line (before double white space) is a song title
                    artist = restOfLine[:restOfLine.find('  ')].upper()     #rest of the line contains artist and year, separated with a double whitespace. We take only portion of the string corresponding to the artist
                artistList = []                                             #create an empty list of artists
                if artist.find('/') != -1:                                  #if there are any occurences of '/' in artist, there are multiple artists for this song
                    artistList.append(artist[:artist.find('/')])            #add the first artist name to the list of artists
                    artistList.append(artist[artist.find('/')+1:])          #add the second artist name to the list of artists
                else:                                                       #otherwise, there is a single artist for the song
                    artistList = [artist]                                   #assign the single artist to artist list
                for artist in artistList:                                   #for each artist corresponding to song
                    if artist in songBank:                                  #if the artist is already in the bank of songs
                        songBank[artist].append(song)                       #append the song to their repertoire
                    else:                                                   #otherwise, this is their first appearance
                        songBank[artist] = [song]                           #create new key for artist, where its value is a list containing their only song
#<------------------------------------------------------------------->
#<- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >



#<- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >
#<----------------------- SETUP THE SERVER SOCKET ----------------------->
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        #create a socket, sock stream lets us make it a tcp connection
setup = False                                                                           #initally, the socket has not successfully been set up
try:                                                                    
    serverSocket.bind(('', 4242))                                                       #binds socket to port 4242 on localhost
    setup = True                                                                        #Sets variable setup to true as we have successfully set up the server socket
    serverSocket.listen(1)                                                              #now listening on this socket, queuing a maximum of 1 request
    logging.info('Server started at '+time.strftime("%H:%M:%S")+                        #write to log file that the server has started
             ' on '+time.strftime("%d/%m/%Y")+'\r\n');                                         
    clientConnected = False                                                             #initially there are no clients connected
except OSError:                                                                         #catch an OSError that may be thrown while trying to bind to a port that is already busy
    print('Cannot bind to port 4242 as it is unavailable / busy')                       #print to the terminal that the port is busy
#<----------------------------------------------------------------------->


#<---------------------- COMMUNICATE WITH CLIENT ------------------------>
while setup:                                                                                #while the server is available to receive requests
    #<------------- WAIT TO RECEIVE CONNECTION REQUEST -------------->
    try:
        clientSocket, address = serverSocket.accept()                                       #accept a request to connect from client
        startTime = time.time()                                                             #capture the time that the connection request was accepted
        clientConnected = True                                                              #set variable client connected to true
        print('Client connected')                                                           #print to the terminal that there is a client connected
        logging.info('Connection successful'+'\r\n')                                        #write to log file that the connection was successful
    except OSError:                                                                         #if there is an exception raised when trying to accept client requests
        logging.info('Connection unsuccessful'+'\r\n')                                      #write to log file that connection was unsuccessful
    logging.info('Client connection request was made at '                                   #write the time of the connection request to a log file
                     +time.strftime("%H:%M:%S")+' on '+time.strftime("%d/%m/%Y")+'\r\n')
    #<--------------------------------------------------------------->

    #<------------- SERVE CLIENT REQUESTS WHILE CONNECTED ----------->
    while clientConnected:                                                                                      #while there is a client connected to the server
        try:
            recvString = clientSocket.recv(1024).decode()                                                       #receive either an artist name or a request to disconnect from the server    
            clientSocket.send('SUCCESS'.encode())                                                               #informs the client that the artist name was received
            if recvString == 'QUIT':                                                                            #if the string received is "quit", this indicates a request from client to disconnect from the server
                raise ConnectionResetError                                                                      #raise a connection reset error to start the process of closing the socket - less redundant code
            else:                                                                                               #otherwise, input string should be considered as a potential artist name
                try:
                    clientSocket.send(str(songBank[recvString]).encode())                                       #attempt to find the songs associated with the artist
                    logging.info('Artist name: '+recvString.title()+'\r\n')                                     #write the artist name to log file
                except KeyError:                                                                                #a key error indicates that the artist does not exist
                    clientSocket.send('KeyError'.encode())                                                      #send 'KeyError' to client to alert them that the artist does not exist
                    logging.info('Artist "'+recvString.title()+'" was requested but does not exist'+'\r\n')     #write to log file the name of the artist even if it does not exist            
        except (ConnectionResetError, BrokenPipeError):                                                         #catch exceptions that are raised when the client forcibly closes the connection
            clientSocket.close()                                                                                #close the communicating socket
            print('Client disconnected \n')                                                                     #print to terminal that the client has disconnected
            logging.info('Time between client connection and disconnection: '                                   #write to log file the time between client connection and disconnection
                             +str(time.time() - startTime)+' seconds'+'\r\n\r\n')                               
            clientConnected = False                                                                             #set variable clientConnected to false to exit while loop
        except OSError:                                                                                         #catches errors occuring when receiving data
            clientSocket.send('FAILURE'.encode())                                                               #informs the client that the artist name was not received which will trigger the client to send it again
        #<--------------------------------------------------------------->
#<----------------------------------------------------------------------->
#<- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >
