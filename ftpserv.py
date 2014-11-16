# *****************************************************
# This file implements a server for receiving the file
# sent using sendfile(). The server receives a file and
# prints it's contents.
# *****************************************************

import socket
import subprocess
import errno
import sys
import os

if len(sys.argv) < 1:
	print ('USAGE python " + sys.argv[0] + " + <port number> ')

# The port on which to listen
listenPort = int(sys.argv[1])

# Create a welcome socket. 
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', listenPort))

# Start listening on the socket
welcomeSock.listen(1)

SUCCESS = "SUCCESS"
FAILURE = "FAILURE"

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):

	# The buffer
	recvBuff = ""
	
	# The temporary buffer
	tmpBuff = ""
	
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		
		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes).decode()
		
		# The other side has closed the socket
		if not tmpBuff:
			break
		
		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	
	return recvBuff



# Accept connections forever
while True:
	
	print ('Waiting for connections...')
	try:	
		# Accept connections
		clientSock, addr = welcomeSock.accept()
		
		print ('Accepted connection from client: ' + str(addr))
		
		clientSock.send('SUCCESS you connected to the server: '.encode())
		msgBuffer =recvAll(clientSock, 10)
		
		choice = recvAll(clientSock, int(msgBuffer))

		while choice != 'quit':

		
			print ('\n')

			#checks to see if the client entered 'put' command
			if choice == 'put':
				msgBuffer =recvAll(clientSock, 10)
				filename = recvAll(clientSock, int(msgBuffer))
				portnumber = clientSock.recv(1024).decode()
				
				port = int(portnumber)
				tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				tempsocket.connect((addr[0], port))
				
				try:



					if filename[-3:] == 'txt':

						outFile = open(filename, 'w')
						# The buffer to all data received from the
						# the client.

						fileData = ""
				
						# The temporary buffer to store the received
						# data.
						recvBuff = ""
					
						# The size of the incoming file
						fileSize = 0	
					
						# The buffer containing the file size
						fileSizeBuff = ""

						# Receive the first 10 bytes indicating the
						# size of the file
						fileSizeBuff = recvAll(tempsocket, 10)
						
						# Get the file size
						fileSize = int(fileSizeBuff)
						
						print ('The file size is ' + str(fileSize))

					
						# Get the file data
						fileData = recvAll(tempsocket, fileSize)
					
						print ('The file data is: ')
						print (fileData)
						outFile.write(fileData)
						outFile.close()
						"""

						DO CODE CLEANUP......
						-all the needless print statements
						-make changes so that file names with spaces can also be read
						-print out the correct amount of file data

						"""


					else:

						
						outFile = open(filename, 'wb')

						fileData = None

						
						
						

						tmepBuff = None
						fileData = tempsocket.recv(1024)
						print ('receiving ' + filename + '...')
						while fileData:
							outFile.write(fileData)
							fileData=tempsocket.recv(1024)



						outFile.close()


				except:
					print(FAILURE)
					outFile.close()
				else:
					print(SUCCESS)


				tempsocket.close()


				#checks to see if the choice is either 'dir' for window users
				#or 'ls' for linux users
			elif choice == 'dir' or choice == 'ls':
				portnumber = clientSock.recv(1024).decode()
				
				port = int(portnumber)
				#creating a temporary socket to use as the data channel
				#and connects to the client's temporary socket
				tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				tempsocket.connect((addr[0],port))
				

				

				TempBuff = ""
				
				#if the choice is 'dir' then run the 'dir' command
				if choice == 'dir':
					status, output =  subprocess.getstatusoutput('dir')
					# check status of command
					if status == 0:
						TempBuff = output
						print(SUCCESS)
					else:
						print(FAILURE)
					
					
				#else if the choice is 'ls' then run the 'ls -l' command
				elif choice == 'ls':
					status, output =  subprocess.getstatusoutput('ls -l')
					if status == 0:
						TempBuff = output
						print(SUCCESS)
					else:
						print(FAILURE)
					
					
				
				
				#get the size of the message to send
				TempBuffSize = str(len(TempBuff))

				#prepend 0's to the message size until it is 10 bytes long
				while len(TempBuffSize) < 10:
					TempBuffSize = "0" + TempBuffSize

				TempBuff = TempBuffSize + TempBuff
				numSent = 0
				#send the message
				while len(TempBuff) > numSent:
					numSent += tempsocket.send(TempBuff[numSent:].encode())
				
				#close the data channel
				
				tempsocket.close()

				
				#else if the choice is 'get' do this
			elif choice == 'get':
				#creates the data channel socket and recv the port number to the client			
				portnumber = clientSock.recv(1024).decode()
				port = int(portnumber)
				tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				tempsocket.connect((addr[0], port))


				
				#the server will recv the file name the client
				#wishes to get from the server
				msgBuffer =recvAll(tempsocket, 10)
				filename = recvAll(tempsocket, int(msgBuffer))
				
				try:
					#opens the desired file if it exists
					if os.access(filename, os.F_OK) == True:
						
						if filename[-3:] == 'txt':

							fileObj = open(filename, "r")

							fileData = None
							
							#keep sending until everything is sent
							while True:

								#read all of the data
								fileData = fileObj.read()

								#if we successfully read something
								if fileData:

									#get the size of the data to read
									dataSizeStr = str(len(fileData))
									print ('Sending: ' + filename)
									print (dataSizeStr + ' bytes to read')
									#prepend 0's to the datasize until its 10 bytes long
									while len(dataSizeStr) < 10:
										dataSizeStr = "0" + dataSizeStr

									#prepend the datasize to the file data
									fileData = dataSizeStr + fileData

									numSent = 0

									#start sending the data
									while len(fileData) > numSent:
										numSent += tempsocket.send(fileData[numSent:].encode())
								
								else:

									break
								print(SUCCESS)
							else:
									print(FAILURE)

						else:

							fileObj = open(filename, "rb")

							fileData = None
							print ('sending: ' + filename)
							fileData = fileObj.read(1024)
							numSent = len(fileData)
							while fileData:
								tempsocket.send(fileData)
								fileData = fileObj.read(1024)
								numSent =numSent + len(fileData)

							print ('Sent: ' + str(numSent) + ' bytes')
							fileObj.close()



					else: print(FAILURE)	
				except:
					print(FAILURE)
			
				tempsocket.close()

			#receive the next choice from the client
			msgBuffer =recvAll(clientSock, 10)
			choice = recvAll(clientSock, int(msgBuffer))
			
			
			
		#Close our side
		clientSock.close()
	except KeyboardInterrupt:
		#if user keys in CTRL+C
		print ('Server Shutting down...')

# Close our side
welcomeSock.close()
	
