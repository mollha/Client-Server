Tested on Mac and Linux
Bash files contain the command python3 instead of python as some of the error handling (e.g. ConnectionRefusedError) was introduced in python 3
Enter ./server.sh into terminal to first run the server
Enter ./client.sh into terminal, the client will automatically connect to the server
If bash files do not work for whatever reason, type into terminal "python3 server.py" and "python3 client.py"
The server will continue to run after client disconnects
It is possible to run multiple instances of the client, however the second client must wait for the first to disconnect before it can communicate with the server
Enter quit to disconnect the client from the server
I did not include the log files as stated in the assignment description as they are automatically generated when the server and client run
