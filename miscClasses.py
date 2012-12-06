# Copyright (c) 2012 Abid Hasan Mujtaba
# See the file LICENSE for copying permission.
#
# Author: Abid H. Mujtaba
# Email: abid.naqvi83@gmail.com
#
# Date: Aug. 10, 2012
#
# 
# This file contains the definitions of miscellaneous classes that are used by the fetchHeaders.py program.



import threading

class Worker( threading.Thread ) :

	'''
	A class inherited from the threading.Thread class which overloads said class to implement an object which maintains a single thread capable of reading tasks from a queue (inQueue) and storing the output of the task to another queue (outQueue) until the inQueue is empty.

	This is a general implementation of this sort of threading paradigm.

	The use of Queue class objects greatly simplifies the asynchronous interaction of threads since the Queue class comes built in with various global locks to prevent chaotic data injection and output. In fact the Queue class's .join() method is an excellent technique for making a program hold off until thread execution completes before moving forward with subsequent code.

	The implementation assumes that the inQueue will finish populating before all tasks are completed or even better that the inQueue is completely populated before execution of the tasks even begins. This is reflected in the break condition for the overloaded run method.
	'''

	def __init__( self, function, inQueue, outQueue ) :

		'''
		'function' is an arbitrary function which accepts a single argument of the type stored in inQueue and returns a (single) output that is stored in outQueue.
		'''
	
		# We are overloading the default .__init__() method of the parent threading.Thread class. Initialize members of the Worker class

		self.function = function
		self.inQueue = inQueue
		self.outQueue = outQueue

		# After having initialized extra members we run the .__init__() script of the parent class (threading.Thread) so that it carries out all tasks necessary for the setting up of a successful thread object

		super( Worker, self ).__init__()

	
	def run( self ) :

		'''
		Overloaded run() method which implements the 2-queue in-Task out-Result thread paradigm.
		'''

		while True :
			
			if self.inQueue.empty() :	# A thread ceases execution when the inQueue is empty. This assumes that the inQueue is fully populated before execution of the threads ends. Usually this means that the inQueue is populated before the task starts.
				
				break


			data = self.inQueue.get()		# Extract data for the task from inQueue

			result = self.function( data )		# Perform task by applying function to the data

			self.outQueue.put( result )		# Store the result in the outQueue

			self.inQueue.task_done()		# Indicates to the inQueue that one of the tasks pulled from the queue has now been completed. This allows the Queue's .join() method to stop blocking when all tasks have been completed.




class Email :		# Struct like object for storing information about a single email. Members can be created on the fly. Each Output object will contain a list of these.

	subject = ''



class Output() :

	'''
	This class stores the information retrieved from each account. It acts as a fancier version of a struct.
	'''

	def __init__( self, settings ) :		# Initialize the account output by storing the account 'settings' dictionary for concurrent use with the lines of output we will be storing

		self.settings = settings	# Store account name in class
		self.emails = []		# Stores the Email objects, one for each email/uid

	



# A class capturing the platform's idea of local time. Code copied from python documentation at http://docs.python.org/library/datetime.html#tzinfo-objects. This bit of code will be coupled with the solution provided by HughE on Jan 15, 2010 (at 12:23) in http://stackoverflow.com/questions/1111317/how-do-i-print-a-python-datetime-in-the-local-timezone to translate server-side timestamps to the clients local time zone so that date and time data makes sense.

from datetime import tzinfo, timedelta, datetime

import time as _time


STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET


class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return timedelta(0)

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0


# End of copied code.



def convertDate( strDate ) :

	'''
	This function accepts the date string as returned by the IMAP server and translates it in to the client's local time (zone) and returns it as a string formatted as desired in the final output.
	'''

	from dateutil.parser import parse as dateParse

	dt = dateParse( strDate.split( '(' ) [0] )		# We perform a split on the left parenthesis for the sometime possibility that the date string ends with something like (GMT-06:00)

	Local = LocalTimezone()		# create an instance of the LocalTimezone class defined above

	ldt = dt.astimezone( Local )

	return ldt.strftime( '%b %d - %I:%M %P' )




def colorText( string, color ) :

	'''
	This function is a wrapper which implements the xterm color model using the simplistic escape codes that wrap text which needs to be output in color. Only the very basic color model is implemented. None of the fancy blinking, bold, underline, .etc is suppored.
	'''

	# We begin by defining the opening and closing escape sequences which we will use to get the correct color wrapper:

	escOpen = "[0;"
	escClose = "[0m"

	# Now we define the dictionary that translates color name strings to number strings that xterm will accept:

	dicColor = {
			'black' : '30',
			'red' : '31',
			'green' : '32',
			'yellow': '33',
			'blue': '34',
			'magenta': '35',
			'cyan': '36',
			'white': '37' }
	
	# And now we output the string with color wrappers surrounding it

	return escOpen + dicColor[ color ] + 'm' + string + escClose




def colorWidth( string, width, color = None, align = '<', fill = True ) :

	'''
	This function is meant to accept a string and limit it to certain (if required space-filled) width whether it is colored or not. If the color provided contains the special value 'None' it indicates that the text is not to be colored.

	color: String for termcolor. 'None' means no color is applied.

	align: [<>^] with '<' being the default. This is the character that specifies the alignment in the string.format command.

	fill: Default value is True. If False is passed then the text is not filled to the specified width by empty space if the width of the text is less than the limit.
	'''

	# Note: When color is applied to text an additional 9 characters are entered around it. These characters don't show up on the screen. However these characters (being of significance to the terminal and NOT to python) are counted when python does string formatting which includes width limitation. This function will implement a method for taking this discrepancy in to account.

	# It does so by truncating and formatting the string before applying the color. That way the color wrapper is not included in the truncation and since the terminal will ignore the wrapper we get the correct width text.

	string = strWidth( string, width, align, fill )		# Truncate string to width
	
	if color :		# This means the text is to be colored

		string = colorText( string, color )		# Function for xterm color wrapper implementation defined above

	return string



def strWidth( string, width, align = '<', fill = True ) :

	'''
	This function is meant to accept a string and limit it to certain (if required space-filled) width.

	align: [<>^] with '<' being the default. This is the character that specified the alignment in the string.format command.

	fill: Default value is True. If False is passed then the text is not filled to the specified width by empty space IF the width of the text is less than the limit. Basically this is a truncation command.
	'''
	
	if fill :
		
		formatString = '{:' + align + str(width) + '.' + str(width) + '}'

		string = formatString.format( string )

	else :
		if len( string ) > width :		# Truncate the string to the specified width

			string = ( '{:' + align + str(width) + '.' + str(width) + '}' ).format( string )

	return string
