#!/usr/bin/python
#
# Copyright (c) 2012 Abid Hasan Mujtaba
# See the file LICENSE for copying permission.
#
# Author: Abid H. Mujtaba
# Email: abid.naqvi83@gmail.com
#
# Start Date: Aug. 9, 2012
# Last Revised: sep. 24, 2012
#
# 
# This script is intended as a program that reads a configuration file and uses the information stored there-in to connect to a variety of IMAP servers and display header information about the emails in various folders (INBOX by default). It also has the capability of deleting selected emails. The advantage is that minimal information needs to be downloaded (i.e. only certain header fields) without needing to download the entire email and one can choose to delete unnecessary emails judging by the sender and/or subject only.


# Create global variables that implement global settings which are used by the following functions.

maxThreads = 5		# This value will be over-written by the global defaul and possibly a command-line argument

colorTitle = None
colorFlag = None
colorFrom = None
colorDate = None
colorSubjectSeen = None
colorSubjectUnseen = None
showFlags = None



def setOptions( configFile, configSpecFile ) :

	'''
	This function reads in the options from the configuration file and validates them using the configuration specification file passed to it. It creates a dictionary of options for each account which are used by the pollAccount() function to carry out its tasks. Additionally this function reads the 'global' section in the configuration file and creates and the globalSettings dictionary that contains the global settings for the program.
	'''

	from configobj import ConfigObj, ConfigObjError, flatten_errors

	from validate import Validator

	# Note the following code segment concerned with using ConfigObj and validating the entries has been inspired and in part copied from http://www.voidspace.org.uk/python/articles/configobj.shtml (an excellent tutorial on using ConfigObj by its author(s))

	try:
		config = ConfigObj( configFile, configspec = configSpecFile, file_error = True )

	except (ConfigObjError, IOError), e:
		
		print 'Could not read "%s": %s' % (configFile, e)

	
	validator = Validator()

	results = config.validate( validator )


	if results != True :		# Validation failed. Inform user of offending entries.

		for (section_list, key, _) in flatten_errors( config, results ) :

			if key is not None :

				print 'The "%s" key in the section "%s" failed validation' % (key, ','.join( section_list ) )

			else :
	
				print 'The following section was missing: %s' % ','.join( section_list )

		import sys

		sys.exit(1)

	# Validation successful so we move on to creating the 'servers' dictionary. We are implementing a default account paradigm which is not natively supported by ConfigObj. We want the ConfigParser ability where any option not provided in a subsection but contained in the 'DEFAULT' subsection are copied in to it. To achieve this we will need to know which entries are missing in each subsection without having them filled in using the default values from the config.spec file. To that end we read in the config file without reading the spec file (hence no spec defaults are read in).

	configNoSpec = ConfigObj( configFile )		# Note since config passed validation we automatically know that configNoSpec is also valid.

	# The first step is to copy out the default account section dictionary and use it as the basic dictionary for all accounts. We will over-write the options that are provided in each account sub-section as we read them.

	listDefaultOptions = configNoSpec[ 'accounts' ][ 'DEFAULT' ].keys()		# List of Default options as EXPLICITLY provided in the configuration file (hence the use of configNoSpec as compared to just config)
	
	listAccounts = [ x for x in config[ 'accounts' ].keys() if x != 'DEFAULT' ]	 		# List of Accounts that does NOT contain 'DEFAULT'. We are basically carrying out list subtraction here: completely removing certain elements from the list by using list comprehension along with a predicate


	# Note: Everywhere a value needs to be read in we must use 'config' and NOT 'configNoSpec' since 'config' by virtue of knowing the required type of each option reads in the values as the correct type rather than as a string which is what we want.

	servers = {}		# Empty dictionary which we will populate with account configuration information

	for account in listAccounts :

		servers[ account ] = {}		# Create sub-dictionary for account
		
		servers[ account ][ 'name' ] = account		# Saving account name for identification and laster use when the sub-dictionary is passed to pollAccount

		for key, value in config[ 'accounts' ][ account ].items() :

			servers[ account ][ key ] = value		# Copy configuration information

		# So far we have stored in the dictionary (for this account) the values specified explicitly and the global defaults from config.spec that are automatically loaded for missing options. Now we must over-write with the options that are not explicitly given but ARE explicitly defined in the 'DEFAULT' section since they carry precedence over the global defaults defined in the config.spec file (which should not ideally be edited by the user but rather represents the creator's fall-back default values in case an option is completely deleted by the user in the config file)
		
		# Now we create a list of the options that are explicitly in DEFAULT but NOT in the specific account (Note the use of configNoSpec rather than config) :

		listMissingDefaults = [ x for x in listDefaultOptions if x not in configNoSpec[ 'accounts' ][ account ].keys() ] 

		for key in listMissingDefaults :

			servers[ account ][ key ] = config[ 'accounts' ][ 'DEFAULT' ][ key ]

	# Now we read in the global settings:

	globalSettings = {}		# Create empty dictionary to populate

	for key in config[ 'global' ].keys() :
		
		globalSettings[ key ] = config[ 'global' ][ key ]
		

	return servers, globalSettings



def argParse() :

	'''
	This function reads in the arguments passed to the program, validates them and if validated returns a parser.parse_args() returned object which contains the various arguments passed and which can then be used by the program as it sees fit.
	'''

	import argparse		# This module gives powerful argument parsing abilities along with auto-generation of --help output.
	
	# Specify the various arguments that the program expects and validate them. Additional arguments can be added as required.

	parser = argparse.ArgumentParser( description = "A python script which simultaneously polls multiple IMAP accounts to display the subjects of all or only unseen messages in the specified folder (INBOX by default) without downloading complete messages.\n For further details please read the man page." )

	parser.add_argument( "-c", "--config", help = "Specify the name and path to the configuration file. If not specified the program will use the default configuration file in $HOME/.fetchheaders/fetchheaders.conf. Note: The configuration specification file (fetchheaders.conf.spec) should not be altered casually and the program will only look for it in $HOME/.fetchheaders/" )

	parser.add_argument( "-a", "--accounts", help = "Specify the names of IMAP accounts to be polled as a comma-separated list. e.g. -a Gmail,Hotmail. Only accounts specified in the configuration file are allowed." )

	parser.add_argument( "-n", "--numsonly", help = "Flag: Only show the number of unseen and total number of messages for the specified folder for each account.", action = "store_true" )

	parser.add_argument( "--noColor", help = "Flag: Do NOT allow colored output. Useful for shells that don't allow colored text or when the output needs to piped to another application since colored text is implemented by encapsulating the text in xterm color escape codes.", action = "store_true" )

	parser.add_argument( "--oldestFirst", help = "Flag: Show oldest email first i.e. chronological order.", action = "store_true" )

	parser.add_argument( "-A", "--showAll", help = "Flag: Show all emails in specified folder, not just unseen ones.", action = "store_true" )

	parser.add_argument( "--showFlags", help = "Flag: Show mutt-style flags (in square brackets) to indicate new/unseen and deleted emails when ALL emails are displayed (i.e. -A is issued).", action = "store_true" )

	parser.add_argument( "-t", "--threads", help = "Specify the maximum number of parallel threads the program will use to simultaneously access IMAP servers. Set to 1 for serial (non-parallel) behaviour.", type = int)


	# Begin reading in arguments and validate them:

	args = parser.parse_args()	# args contains the values of arguments passed. If incorrect arguments are passed the problem will be stopped here and argparse will display the appropriate error and help message.

	return args



def applyArgs( args, servers, globalSettings ) :

	'''
	This function accepts both the arguments read by the script and the 'servers' object (dictionary) created by setOptions(). It will apply the arguments sent via command-line to the 'servers' and 'globalSettings' object to create and return a modified version reflecting these changes.
	'''
	
	# This function is where we carry out all operations necessary to implement the settings specified by command-line arguments.


	# -a, --acounts. Limit accounts to the specified ones:

	if args.accounts :	# True if -a or --accounts has been specified
		
		# We must perform some error checking on the arguments passed to the --acounts optional argument

		newServers = {}		# Create a new dictionary we will populate ONLY with the specified accounts

		for item in args.accounts.split( ',' ) :	# We are expecting a comma-separated list

			if not item in servers.keys() :		# If one of the items in the comma-separated list is NOT an account specified in the configuration file

				print( '\nError: ' + item + ' is not a valid IMAP account name specified in the configruation file.' )

				import sys

				sys.exit(1)

			else :

				newServers[ item ] = servers[ item ]

		servers = newServers

	
	# -n, --numsonly. If specified only the total and unseen number of messages is to be displayed. Similar to 'fetchmail -c'.

	if args.numsonly :

		for account in servers.keys() :

			servers[ account ][ 'showOnlyNums' ] = True


	# --no-color. If specified the output of the program should NOT be colored.

	if args.noColor :
		
		globalSettings[ 'color' ] = False
	

	# -A, --showAll. Show all emails not just unseen ones.

	if args.showAll :

		for account in servers.keys() :

			servers[ account ][ 'showUnseen' ] = False
	

	# --oldestFirst. Show oldest email first i.e. in chronological order.

	if args.oldestFirst :

		for account in servers.keys() :

			servers[ account ][ 'latestEmailFirst' ] = False
	

	# --showFlags. Show mutt-style flags (in square brackets) when all emails are being displayed.

	if args.showFlags :
		
		globalSettings[ 'showFlags' ] = True


	# -t, --threads. Set max. number of parallel threads.

	if args.threads :

		globalSettings[ 'maxThreads' ] = args.threads

	

	return servers, globalSettings
	


def applyGlobalSettings( globalSettings ) :

	'''
	This function applies the global settings defined in the dictionary 'globalSettings' (created using the configuration file and command-line arguments).
	'''

	# Apply maxThreads setting:

	global maxThreads

	maxThreads = globalSettings[ 'maxThreads' ]


	# Apply showFlags settings:

	global showFlags

	showFlags = globalSettings[ 'showFlags' ]


	# Apply color settings:

	if globalSettings[ 'color' ] :		# output is to be colored

		global colorTitle, colorFlag, colorDate, colorFrom, colorSubjectSeen, colorSubjectUnseen		# Accessing global text color variables

		colorTitle = globalSettings[ 'colorTitle' ]
		colorFlag = globalSettings[ 'colorFlag' ]
		colorSubjectSeen = globalSettings[ 'colorSubjectSeen' ]
		colorSubjectUnseen = globalSettings[ 'colorSubjectUnseen' ]
		colorDate = globalSettings[ 'colorDate' ]
		colorFrom = globalSettings[ 'colorFrom' ]



def pollAccount( account ) :

	'''
	This function accepts a dictionary associated with a SINGLE account (a particular email address on a particular imap server) and carries out all the actions required to connect with said account (poll it) and get email information AND display it.
	'''

	# Note: The way this function is currently constructed it produces no direct ouput to stdout but rather stores it in a buffer class object which it returns. The calling function decides when to display the information. This has been done to facilitate the parallelizing of polling of the accounts.

	from imapServer import imapServer
	import re
	from miscClasses import colorWidth as cW	# Custom function that sets width of text fields and colors it.

	numUnseen = -1		# Set unequal to zero in case showNums = False


	from miscClasses import buffer

	buf = buffer()		# Create print buffer

	
	mail = imapServer( account['host'] )

	mail.login( account['username'], account['password'] )

	mail.examine()


	buf.bprint0( cW( account['name'] + ':', 12, colorTitle ) ) 

	
	if account[ 'showNums' ] :

		(numAll, numUnseen) = mail.numMsgs()

		buf.bprint( '( total: ' + str( numAll ) + ' | unseen: ' + str( numUnseen ) + ' )\n' )


	if not account[ 'showOnlyNums' ] :


		from miscClasses import convertDate		# Custom function that converts imap returned date string to the format required

		if account[ 'showUnseen' ] :		# show only unseen emails from the folder
		
			ids = mail.getUids( "unseen" )

		else :

			ids = mail.getUids( "all" )


		data = mail.fetchHeaders( ids, ['from', 'subject', 'date'] )



		# We configure the behaviour of the program by creating anonymous (lambda functions) which we choose on the basis of configuration choices. This means that the test need only be performed once.

		if account[ 'latestEmailFirst' ] :		# We define an anonymous function that modifies the order in which we access UIDs based on the configuration.

			orderUid = lambda ii: len( ids ) - 1 - ii	# Access UIDs in reverse order since the latest email has the largest UID

		else :

			orderUid = lambda ii: ii			# Access emails in ascending order of UID which corresponds to latest email last



		if len(ids) > 100 :		# Get number of digits of total number of messages.

			return str( len( str( len(ids) ) ) )		# Used to get number of digits in the number for total number of messages. Crude Hack at best.
		else :

			numDigits = '2'



		if account[ 'showUnseen' ] :		# Show only unseen messages


			for ii in range( len( ids ) ) :
		
				uid = ids[ orderUid( ii ) ]
		
				line = data[ uid ]		
		
				strFrom = line[ 'from' ]
		
				m = re.match( '\"?([^<]*?)\"? <.*', strFrom )
		
				if m:
		
					strFrom = m.group(1)


				# Now we extract the date from the header information and place it in the output format we want. The fucntionality has been encoded in a separate function:

				strDate = convertDate( line[ 'date' ] )
		
				buf.bprint( cW( str(ii + 1), numDigits, align = '>' ) + '.  ' + cW( strDate, 17, colorDate ) + '    ' + cW( strFrom, 30, colorFrom ) + '   ' + cW( line['subject'], 120, colorSubjectUnseen, fill = False ) )


		else :		# Show all messages

			dicFlags = mail.fetchFlags( ids )		# Get flags for each message so that we can distinguish between seen and unseen messages

			reSeen = re.compile( '.*Seen.*' )


			if showFlags :		# If so configured we display the flag associated with each message.
				
				flags = lambda x : '  [ ' + cW( x, 2, colorFlag ) + ']   '

			else :

				flags = lambda x : '.   '


			for ii in range( len( ids ) ) :

				uid = ids[ orderUid( ii ) ]

				line = data[ uid ]

				strFrom = ( '{:<30.30}' ).format( line[ 'from' ] )

				m = re.match( '\"?([^<]*?)\"? <.*', strFrom )
		
				if m:
		
					strFrom = m.group(1)

				# Now we extract the date from the header information.

				strDate = convertDate( line[ 'date' ] )

				# Now we use the flags to distinguish betweeen seen and unseen messages:

				m = reSeen.match( dicFlags[ uid ] )

				if m :		# Flag has a Seen flag. We change color.
		
					flag = ' '
					colorSubject = colorSubjectSeen

				else :
					
					flag = 'N'
					colorSubject = colorSubjectUnseen


				buf.bprint( cW( str(ii + 1), numDigits, align = '>' ) + flags( flag ) + cW( strDate, 17, colorDate ) + '    ' + cW( strFrom, 30, colorFrom ) + '   ' + cW( line['subject'], 120, colorSubject ) ) 
	
	mail.logout()

	return buf



def threadedExec( servers ) :

	'''
	This implements the program using a threaded queue model
	'''

	from Queue import Queue

	inQueue = Queue()	# Initiate and populate input queue with list of tasks (data for each task)

	for account in servers :

		inQueue.put( servers[ account ] )		# Store the account dictionary in inQueue. This denotes the data required for a single task: polling a single server

	outQueue = Queue( maxsize = inQueue.qsize() )		# Prepare output queue for storing results

	# Create a number of threads to parallelize the tasks. Threads created using the Worker class inherited from the threading.Thread class:
	
	from miscClasses import Worker		# import the inherited threading class


	workers = [ Worker( pollAccount, inQueue, outQueue ) for ii in range( maxThreads ) ]		# maxThreads is a global variable that determines the maximum number of open threads

	for worker in workers :

		worker.start()		# Begun execution of the thread


	inQueue.join()		# Pause program stepping forward here until all tasks in inQueue are completed

	
	while not outQueue.empty() :

		yield outQueue.get()		# this wording makes test3() a generator and it should be used as such. test3 will return Buffer type objects from each server poll one at a time.



def main() :

	'''
	Main function that starts the execution of all of the code.
	'''

	args = argParse()

	# Specify default locations for configuration and specification files:

	import os

	homeFolder = os.getenv( "HOME" )	# Basically the value in $HOME

	fileConf = homeFolder + '/.fetchheaders/fetchheaders.conf'
	fileSpec = homeFolder + '/.fetchheaders/fetchheaders.conf.spec'

	# Check if a configuration file has been specified using the -c or --config flag.

	if args.config :		# A configuration file has been provided

		fileConf = args.config


	# Read in settings and options from configuration files :

	servers, globalSettings = setOptions( fileConf, fileSpec )

	
	# Override settings and options from command-line arguments :

	servers, globalSettings = applyArgs( args, servers, globalSettings )
	
	
	# Apply Global Settings. These are applied outside of pollAccount which acts on each account independantly.

	applyGlobalSettings( globalSettings ) 		# Apply the global settings contained in the 'globalSettings' dictionary we created from the configuration file and command-line arguments


	# Begin threaded execution of accessing accounts:

	for buf in threadedExec( servers ) :

		print( '\n' )

		buf.dump()



# Main execution of the program begins here:

main()
