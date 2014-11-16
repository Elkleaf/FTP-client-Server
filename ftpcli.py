# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys
import subprocess

# Command line checks 
if len(sys.argv) < 2:
	print ('USAGE python " + sys.argv[0] + " + <server_machine> + <port number> ') 

# Server address
serverAddr = sys.argv[1]

# Server port
serverPort = int(sys.argv[2])

# The name of the file
#fileName = sys.argv[3]

# Open the file
#fileObj = open(fileName, "r")
choice = []
# Create a TCP socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
connSock.connect((serverAddr, serverPort))
print (connSock.recv(1024).decode() + serverAddr)
	
#print ("successfully connected to " + serverAddr)

#grab user input 
temp = input('ftp>')
# *****************************************
#split the user input into a list of words
#so it is easier identify the commands from
#the file name
# *****************************************
choice = temp.split()


while choice[0] != 'quit':
	
	
	
	if choice[0] == 'put':
	
		#sending the choice over the control channel
		#to the server
		msgSize = str(len(choice[0]))
		while len(msgSize) < 10:
			msgSize = "0" + msgSize

		choice[0] = msgSize + choice[0]
		connSock.send(choice[0].encode())

		fileName = choice[1]
		

		msgSize = str(len(choice[1]))
		while len(msgSize) < 10:
			msgSize = "0" + msgSize

		choice[1] = msgSize + choice[1]
		connSock.send(choice[1].encode())
		
		
		# ************************************************************************
		#creates a new temporary socket that will be used to transfer data between
		#server and client. We bind the socket to port '0' and then retrieve the
		#ephemeral port number
		# ************************************************************************
		tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tempsocket.bind(('',0))
		portnumber = tempsocket.getsockname()[1]
		
		tempsocket.listen(1)
		connSock.send(str(portnumber).encode())


		Datasock, tempaddr = tempsocket.accept()

		"""

		DO CODE CLEANUP......
		-all the needless print statements
		-make changes so that file names with spaces can also be read
		-print out the correct amount of file data

		"""
				
		#number of bytes sent
		numSent = 0

		if os.access(fileName, os.F_OK) == True:

			if fileName[-3:] != 'txt':

				fileObj = open(fileName, 'rb')

				fileData = None
				
				fileData = fileObj.read(1024)
				numSent = len(fileData)
				print('uploading file ' + fileName +'...')
				while fileData:
					Datasock.send(fileData)
					fileData = fileObj.read(1024)
					numSent = numSent + len(fileData)





			else:

				fileObj = open(fileName, 'r')
			
				# The file data
				fileData = None

				# Keep sending until all is sent
				while True:

				
					# Read all of the data
					fileData = fileObj.read()
				
					# Make sure we did not hit EOF
					if fileData:
					
						
						# Get the size of the data read
						# and convert it to string
						dataSizeStr = str(len(fileData))
						print (dataSizeStr)
						# Prepend 0's to the size string
						# until the size is 10 bytes
						while len(dataSizeStr) < 10:
							dataSizeStr = "0" + dataSizeStr
				
				
						# Prepend the size of the data to the
						# file data.
						fileData = dataSizeStr + fileData	
					
						# The number of bytes sent
						numSent = 0
					
						# Send the data!
						while len(fileData) > numSent:
							numSent += Datasock.send(fileData[numSent:].encode())
				
					# The file has been read. We are done
					else:
					
						break

			#print the number of bytes sent and close the file and 
			#the temporarysocket
			print ('Sent the file: '+ fileName + ' and sent ' + str(numSent) + ' bytes.')
			Datasock.close()
			tempsocket.close()

			fileObj.close()

		else:
			print ('File ' + fileName + ' was not sent')
			Datasock.close()
			tempsocket.close()


	elif choice[0] == 'dir' or choice[0] == 'ls':
		#send the client choice over the control channel
		msgSize = str(len(choice[0]))
		while len(msgSize) < 10:
			msgSize = "0" + msgSize

		choice[0] = msgSize + choice[0]
		connSock.send(choice[0].encode())
		

		#creates a temporary socket to use as the data channel
		tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tempsocket.bind(('',0))
		portnumber = tempsocket.getsockname()[1]
		
		tempsocket.listen(1)
		connSock.send(str(portnumber).encode())

		Datasock, tempaddr = tempsocket.accept()
		
		
		
		MsgsizeBuff = ""
		tempBuff = ""

		#this while loop will just get the size of the message which is 
		#contained in the first 10 bytes, so this will just
		#read up to 10 bytes of the message
		while len(MsgsizeBuff) < 10:
			tempBuff = Datasock.recv(10).decode()

			if not tempBuff:
				break

			MsgsizeBuff += tempBuff

		
		Msgsize = int(MsgsizeBuff)
		recBuff = ""
		
		#this while loop will read the rest of the message
		# now that we know how big the messge is
		while len(recBuff) < Msgsize: 
			recBuff += Datasock.recv(Msgsize).decode()

			if not recBuff:
				break

		print (recBuff)
		Datasock.close()
		tempsocket.close()

	elif choice[0] == 'get':

		#same thing as before, sending the choice to the
		#server over the control channel
		msgSize = str(len(choice[0]))
		while len(msgSize) < 10:
			msgSize = "0" + msgSize

		choice[0] = msgSize + choice[0]
		connSock.send(choice[0].encode())
		

		#creating the data channle socket
		tempsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tempsocket.bind(('',0))
		portnumber = tempsocket.getsockname()[1]
		tempsocket.listen(1)
		connSock.send(str(portnumber).encode())

		Datasock, tempaddr = tempsocket.accept()

		
		FileName = choice[1]
		#sending the filename to get
		msgSize = str(len(choice[1]))
		while len(msgSize) < 10:
			msgSize = "0" + msgSize

		choice[1] = msgSize + choice[1]
		Datasock.send(choice[1].encode())


		if FileName[-3:] == 'txt':

			tempbuff = ""
			fileData = ""

			filesize = 0

			fileSizeBuff = ""

			
			#gets the size of the message
			while len(fileSizeBuff) < 10:

				tempbuff = Datasock.recv(10).decode()

				if not tempbuff:
					break

				fileSizeBuff += tempbuff
				
			if len(fileSizeBuff) != 0:
				filesize = int(fileSizeBuff)


				#creates an output file to write the data to
				outFile = open(FileName, 'w')

				print ('The file size of ' + FileName + ' is: ' + str((filesize)))

				tempbuff = ""
				
				#reads the rest of the message now that
				#we know the size of the message
				while len(fileData) < filesize:

					tempbuff = Datasock.recv(filesize).decode()

					if not tempbuff:
						break

					fileData += tempbuff

				outFile.write(fileData)
				outFile.close()
			Datasock.close()
			tempsocket.close()

			print ('Received  '+ str(filesize) + ' bytes of  file ' + FileName + '')

		else:
			outFile = open(FileName, "wb")

			fileData = None

			fileData = Datasock.recv(1024)
			numRec = len(fileData)
			print('downloading ' + FileName + '...')
			while fileData:
				outFile.write(fileData)
				fileData = Datasock.recv(1024)
				numRec = numRec + len(fileData)

			outFile.close()
			Datasock.close()
			tempsocket.close()

			print ('received ' + str(numRec) + ' bytes')

	

	#we read the user's choice again at the end of the while loop
	#so we can correctly compare the user's next choice
	temp = input('ftp>')
	choice = temp.split()
	
	#if the user chooses quit, we need to send 
	#the 'quit' choice to the server before we exit
	#the loop so that way the server will know the client
	#is quiting and will no longer be sending or receiving 

msgSize = str(len(choice[0]))
while len(msgSize) < 10:
	msgSize = "0" + msgSize

choice[0] = msgSize + choice[0]
connSock.send(choice[0].encode())

# Close the socket and the file
connSock.close()
	

	


