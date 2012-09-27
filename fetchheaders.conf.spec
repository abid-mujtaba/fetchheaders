# This is the Configuration Specification file used by Python's ConfigObj module. This closely mirros the fetchheaders.conf configuration file. Its intent is to specify the type and default value for the various options allowing for validation of the user-editted actual configuration file.
#
# CAUTION: It is advised that this file not be editted unless absolutely necessary. The defaults set here are by the programmer and should be over-written in the actual configuration file (fetchheaders.conf).
#
# These default values come in to play only if a option is completely omitted from the actual configuration file and represent the programmer's fall-back default values.
#
# Changing anything but the defaults, especially, deleting any entries may cause the program to stop functioning properly. Only power-users (and only those who understand the program's functionality) should play around with these settings.

[accounts]

	[[__many__]]
	
	host = string( default = None )
	username = string( default = None )
	password = string( default = None )
	showUnseen = boolean( default = True )
	folder = string( default = 'INBOX' )
	latestEmailFirst = boolean( default = True )
	showNums = boolean( default = True )
	showOnlyNums = boolean( default = False )


[global]
	
	maxThreads = integer( default = 5 )
	
	color = boolean( default = True )
	colorTitle = string( default = 'blue' )
	colorFlag = string( default = 'red' )
	colorDate = string( default = 'yellow' )
	colorFrom = string( default = 'cyan' )
	colorSubjectSeen = string( default = 'yellow' )
	colorSubjectUnseen = string( default = 'green' )
	showFlags = boolean( default = False )
