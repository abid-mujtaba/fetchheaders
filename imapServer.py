#! /usr/bin/python
#
# Copyright (c) 2012 Abid Hasan Mujtaba
# See the file LICENSE for copying permission.
#
# Author: Abid H. Mujtaba
# Email: abid.naqvi83@gmail.com
#
# Date: Aug. 7, 2012
#
# This script uses the 'imaplib' module to access a number of specified imap servers and display the subjects of emails in the INBOX folder.
#
# The script implements a wrapper class for imaplib specifically tailored to the fetchHeaders application.



class imapServer: 	# This class implements all the functionality we need from the interface with a given imap server. It forms a wrapper around the 'imaplib' module.

	def __init__( self, server ) :

		'''
		This is the constructor function for this class. It requires the servername in the form of a string.

		Note: All connections will be made using SSL so only SSL enabled imap servers are accessible.
		'''

		self.server = server
		
		import imaplib		# Import the crucial module that allows interaction with IMAP servers	

		try :
			self.mail = imaplib.IMAP4_SSL( self.server )		# Establish connection with the server.

		except:
			print( 'Unable to establish SSL connection to IMAP server ' + self.server )



	def login( self, username, password ) :

		'''
		Method for sending credentials to IMAP server for logging in.
		'''

		self.username = username	# Saving credentials in object as members.
		self.password = password
	
		try: 
			self.mail.login( self.username, self.password )

		except:
			print( 'Credentials (username and password) rejected by IMAP server (or connection lost).' )
	

	
	def logout( self ) :

		'''
		Method for closing the selected folder and logging out of the IMAP server.
		'''

		try:
			self.mail.close()
			self.mail.logout()

		except:
			print( 'Unable to successfully logout of IMAP server.' )

	

	def select( self, folder = "INBOX" ) :

		'''
		Method for selecting a paticular folder on the imap server. The Inbox is the default option.

		The folder must be specified as a string according to the IMAP protocols (the string you would use when connecting using imaplib or telnet (openssl). A list of the folders one can access can be listed using the .listFolders() method.
		'''

		self.folder = folder

		try: 
			self.mail.select( self.folder )
	
		except:
			print( 'Unable to select folder ' + self.folder + ' in IMAP server.' )
	



	def examine( self, folder = 'INBOX' ) :

		'''
		Method for examining a particular folder. This differs from 'select' in that it is purely readonly, not even the flags (such as 'SEEN') are altered by choosing a folder using 'examine'.

		The folder must be specified as a string according to the IMAP protocols (see .select() above).
		'''

		self.folder = folder

		try:
			self.mail.select( self.folder, readonly = True )

		except:
			print( 'Unable to examine folder ' + self.folder + ' in IMAP server.' )




	def listFolders( self ) :

		'''
		Method lists all the folders in the account on the imap server. The output is a raw string.

		The method assumes that self.login() has been called i.e. self.mail is currently connected to the user's account.
		'''

		try:
			tmpList = self.mail.list()[1]		# The first member of list() is the result of the attempt. 'OK' if successful. The second member is the list.
		except:
			print( 'Unable to list folders in account' )


		return tmpList




	def totalMsgs( self ) :

		'''
		Method to return total number of messages in currently selected folder.
		'''

		try:
			tmpStr = self.mail.status( self.folder, "(messages)" )[1][0]	  # status returns list of lists with us needing the first element of the second list

		except:
			print( 'Unable to receive total number of messages in folder: ' + self.folder )

		else:
			return int( _substring( '.*MESSAGES ([0-9]*).*', tmpStr ) )		# Returned as an integer NOT a string
	



	def unseenMsgs( self ) :

		'''
		Method to return number of unseen messages in currently selected folder.
		'''

		try:
			tmpStr = self.mail.status( self.folder, "(unseen)" )[1][0]

		except:
			print( 'Unable to receive number of unseen messages in folder: ' + self.folder )

		else:
			return int( _substring( ".*UNSEEN ([0-9]*).*", tmpStr ) )


	
	def numMsgs( self ) :

		'''
		Method to return both the number of total messages and unseen messages in one go as a tuple of form (total, unseen).
		'''

		try:
			tmpStr = self.mail.status( self.folder, "(messages unseen)" )[1][0]

		except:
			print( 'Unable to receive number of total and unseen messages in folder: ' + self.folder )

		else:

			numAll = int( _substring( '.*MESSAGES ([0-9]*).*', tmpStr ) )
			numUnseen = int( _substring( '.*UNSEEN ([0-9]*).*', tmpStr ) )

			return (numAll, numUnseen)
	


	def getUids( self, strSearch ) :

		'''
		Method to return the unique UIDs of emails from current folder based upon the status of certain flags as specified by 'strSearch'. The method has the ability to return the UIDs of all messages or just unseen messages .etc.

		strSearch excepts all of the strings accepted by the SEARCH method in the IMAP protocol. We will mostly be working with "ALL" and "UNSEEN".
		'''

		try:
			return self.mail.uid( 'search', None, strSearch )[1][0].split()		# This generates a list of UIDs as strings containing integers only.

		except:
			print( 'Unable to retrieve UIDs of emails specified by strSearch from IMAP server in folder: ' + self.folder )

	


	def fetchHeaders( self, lstUIDs, lstFields = ['from', 'subject'] ) :

		'''
		Method to fetch fields specified by the list of strings 'lstFields' of the emails whose UIDs are in the list 'lstUIDs' from the current folder.

		lstUIDs is a list of UIDs, each UID being a string containing an integer.

		lstFields is a list of strings specifying the HEADER fields that fetch will use to extract information from the specified emails. A common example for fetching just 'from' and 'subject' fields is ['From', 'Subject']. The first letter of each field string must be uppercase and all the latter ones need to be in lowercase.

		The output of this method is a dictionary of dictonaries. Each UID is associated with a dictionary where the keys are the values of lstFields.
		'''

		import re

		# We will retrieve each field one at a time. This will increase the internet load but will make it much easier for us to deal with the information that we get since we won't have to parse the information.

		output = {}

		for item in lstUIDs :	output[ item ] = {}	# Initiate the output dictionary of dictionaries

		for field in lstFields :

			try :
				data = self.mail.uid( 'fetch', ','.join( lstUIDs ), '(BODY[HEADER.FIELDS (' + field + ')])' )[1]

			except:
				print( 'Unable to fetch field ' + field + ' from folder ' + self.folder )

			else :
				
				for ii in range( len( lstUIDs ) ) :
					
					uid = lstUIDs[ii]

					# Remove the field name from data using Regex. This requires us to put 'field' in to pascal case.

					pField = field[0].upper() + field[1:].lower()	# Convert to Pascal case

					string = data[ 2 * ii ][1]

					string = _reduceWhitespace( string )

					m = re.match( pField + ': (.*)', string ) 

					if m :
						output[ uid ][ field ] = m.group(1)

					else :
						output[ uid ][ field ] = 'RegEx Error: ' + string

		return output




	def fetchFlags( self, lstUIDs ) :

		'''
		Method for fetching flags for the specified emails.
		'''

		output = {}	# Create empty dictionary

		try :
			data = self.mail.uid( 'fetch', ','.join( lstUIDs ), 'flags' )[1]

		except :
			print( 'Unable to fetch flags for specified emails.' )

		else :
			import re

			for item in data :

				m = re.match( '.*UID ([0-9]*)[^\(]*\(([^\)]*).*', item )

				if m:
					output[ m.group(1) ] = m.group(2)

			return output




	def fetch( self, lstUIDs, strFetch ) :

		'''
		Wrapper method for the IMAP 'fetch' command. This accepts the standard string used in an IMAP 'fetch' request, along with a list of UIDs identifying the emails for which the fetch request will be carried out. The output is the raw unformatted, unfiltered text that is returned by the server.

		The standard request to get just 'From' and 'Subject' fields is to use strFetch = '(BODY[HEADER.FIELDS (from subject)])'
		'''

		try :
			return self.mail.uid( 'fetch', ','.join( lstUIDs ), strFetch )[1]
		
		except :
			print( 'Unable to fetch (raw) fields for emails from folder ' + self.folder )

	

	def copy( self, lstUIDs, folder ) :

		'''
		Method copyies the emails specified by list 'lstUIDs' to the specified folder (a string). This method will work with EXAMINE as well as SELECT.
		'''

		try :
			self.mail.uid( 'copy', ','.join( lstUIDs ), folder )

		except :
			print( 'Unable to copy specified emails to folder ' + folder + '.' )




	def delete( self, lstUIDs ) :

		'''
		Method marks the emails specified by list lstUIDs for deletion by setting the \Deleted flag.

		Note: The emails won't actually be deleted until the .logout or .expunge method is called.
		'''

		try :
			self.mail.uid( 'STORE', ','.join( lstUIDs ), '+FLAGS', '(\Deleted)' )		# The command wouldn't work without putting some of the strings in all caps

		except :
			print( 'Unable to set \Deleted flags on specified emails.' )



	
	def expunge( self ) :

		'''
		Method calls the IMAP expunge command which permenantly deletes any emails marked for deletion in the current folder.
		'''

		self.mail.expunge()




def _substring( pattern, string ) :

	'''
	This is a hidden external function in this module which is used to extract a specific substring of a string based on a pattern supplied. The pattern is regex where the first group specified will be returned.
	'''

	import re

	m = re.match( pattern, string )

	if m:				# Match was succesful
		return m.group(1)

	else :
		return None


def _reduceWhitespace( string ) :

	'''
	This is a hidden external function that is meant to be applied on strings returned by the imap server. Its intent is to remove '\r' and '\n', replace '\t' with a single space and reduce any occurence of more than one consecutive space with a single space. It achieves this using regular expressions and the substitute command.
	'''
	
	import re

	return re.sub( ' \s*', ' ', re.sub( '\t', ' ', re.sub( '[\r|\n]', '', string ) ) )
