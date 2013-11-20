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


def pollAccount( account ) :

    """
    This function accepts a dictionary associated with a SINGLE account (a particular email address on a particular imap server) and carries out all the actions required to connect with said account (poll it) and get email information AND display it.
    """

    # Note: The way this function is currently constructed it produces no direct ouput to stdout but rather stores it in a buffer class object which it returns. The calling function decides when to display the information. This has been done to facilitate the parallelizing of polling of the accounts.

    from imapServer import imapServer
    import re
    from copy import deepcopy

    cW = colorWidth		# Rename function for easier typing and clarity


    numUnseen = -1		# Set unequal to zero in case showNums = False


    mail = imapServer( account['host'] )

    mail.login( account['username'], account['password'] )

    mail.examine()


    out = Output( account )		# Create Output data structure for imminent population



    if account[ 'showNums' ] :

        try:
            (numAll, numUnseen) = mail.numMsgs()

        except TypeError:           # This happens if an error occurred in connecting to the server and so numMsgs() returns a NoneType object

            out.error = True

            return out              # In this case we return out with the error flag set to True

        out.numAll = numAll		# Store numbers in output object
        out.numUnseen = numUnseen


    if not account[ 'showOnlyNums' ] :


        if account[ 'showUnseen' ] :		# show only unseen emails from the folder

            ids = mail.getUids( "unseen" )

        else :

            ids = mail.getUids( "all" )


        out.uids = deepcopy( ids )		# Store the UIDs of the emails retrieived in the general output object


        if len( ids ) > 0 :		# There has to be at least one email to fetch data or otherwise fetchHeaders will throw up an error


            data = mail.fetchHeaders( ids, ['from', 'subject', 'date'] )


            if account[ 'latestEmailFirst' ] :		# We define an anonymous function that modifies the order in which we access UIDs based on the configuration.

                ids.reverse()
                out.uids.reverse()		# We must also flip the order in which the uids are stored so that the lines and uids match


            if len(ids) > 100 :		# Get number of digits of total number of messages.

                numDigits = len( str( len(ids) ) )		# Used to get number of digits in the number for total number of messages. Crude Hack at best.
            else :

                numDigits = 2

            out.numDigits = numDigits		# Store the number of digits in the object related to the account


            reFrom = re.compile( '\"?([^<]*?)\"? <.*' )

            # We begin by scanning all of the the uids extracted and storing the information in the Output object 'out':

            for uid in ids :

                email = Email()		# Create a new Email object for insertion in out.emails

                line = data[ uid ]

                strFrom = '{:<30.30}'.format( line[ 'from' ] )

                m = reFrom.match( strFrom )

                if m:
                    strFrom = m.group(1)

                email.From = strFrom
                email.Date = convertDate( line[ 'date' ] )
                email.Subject = line[ 'subject' ]

                email.uid = uid		# Store the email's uid along with it for later usage

                out.emails.append( email )


            # If we are dealing with all emails we may need additional information stored in 'out'

            if not account[ 'showUnseen' ] :		# this means we are displaying ALL emails, seen and unseen

                dicFlags = mail.fetchFlags( ids )

                reSeen = re.compile( '.*Seen.*' )

                for ii in range( len( ids ) ) :

                    m = reSeen.match( dicFlags[ ids[ ii ] ] )

                    if m :		# Flag has a Seen flag. We store that information in 'out'

                        out.emails[ ii ].Seen = True

                    else :
                        out.emails[ ii ].Seen = False

            else :		# We are displaying only unSeen messages

                for ii in range( len( ids ) ) :

                    out.emails[ ii ].Seen = False		# Message is necessarily Unseen


    mail.logout()

    return out		# Return the Output data structure we have just populated




def deleteEmails( account, listUIDs ) :

    '''
    This function deletes specified emails from a single account. It is meant to be called by a multi-thread execution routine for each account required.

    account: <DICTIONARY> Contains the settings associated with a particular account. Used to login to said account.

    listUIDs: <LIST> of <INTEGERS>. Contains the UIDs of the emails that are to be deleted from the specified account.
    '''


    trashFolder = account[ 'trashFolder' ]		# Get name of Trash Folder associated with specified account

    flagDeleteEmails = account[ 'deleteEmails' ]		# Get boolean flag which indicates whether emails actually need to be physically deleted, or just copied.


    from imapServer import imapServer

    mail = imapServer( account['host'] )

    mail.login( account['username'], account['password'] )

    mail.select()

    # Now we have accessed the proper folder:

    # First we copy the emails to the Trash folder:

    mail.copy( listUIDs, trashFolder )		# We send the list of UIDs and the name of the trash folder to mail.copy() so that these emails can be copied in to the Trash Folder


    if flagDeleteEmails :			# If the account setting indicates that emails are to be deleted after copying. Set to False for Gmail accounts.

        mail.delete( listUIDs )		# Provide mail.delete with list of UIDs. The method flags the emails for deletion on the IMAP server.

        mail.expunge()			# This tells the IMAP server to actually delete the emails flagged as such


    mail.logout()			# Logout gracefully from the account







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




class delWorker( threading.Thread ) :

    '''
    This is a class that implements a multi-threaded paradigm based on a single queue and a function that needs to be applied to said objects. No output is produced.

    This is a custom implementation with the class repsonsible for taking objects from the inQueue, splitting off into two parts and passing these parts to the appropriate function.

    The purpose of each worker is to read accounts and UID lists from the inQueue and call the deleteEmails() function upon them.
    '''

    def __init__( self, inQueue ) :

        '''
        inQueue: <Queue Object> Contains dictionaries, each with two parts: 'account' <DIC> associated with each email account and 'listUIDs' list of UIDs of emails to be deleted.
        '''

        self.function = deleteEmails		# Store the above defined deleteEmails as the function to be applied. This takes in two parameters: dictionary of account settings and list of UIDs.

        self.inQueue = inQueue

        # After having performed customized start up we call the .__ini__() script of the parent class (threading.Thread) to carry out tasks necessary for setting up threading.

        super( delWorker, self ).__init__()



    def run( self ) :

        '''
        Overloaded run() method which implements the single queue thread paradigm.
        '''

        while True :

            if self.inQueue.empty() :		# No more tasks left in queue. The delWorker should cease execution of tasks

                break


            data = self.inQueue.get()		# Extract data for task from inQueue

            self.function( data[ 'account' ], data[ 'listUIDs' ] )		# Perform task using data and the function associated with the task. In this case delete specified emails from specified account


            self.inQueue.task_done()		# Inform the inQueue that an extracted task has been completed. This allows the inQueue to know when all tasks have been completed.









class Email :		# Struct like object for storing information about a single email. Members can be created on the fly. Each Output object will contain a list of these.

    subject = ''



def threadedExec( servers, maxThreads ) :

    '''
    This implements the email account access part of the program using a threaded queue model

    maxThreads in an INTEGER that denotes the maximum number of parallel threads that the program is allowed to open. This is a global setting.
    '''

    from Queue import Queue

    inQueue = Queue()	# Initiate and populate input queue with list of tasks (data for each task)

    for account in servers :

        inQueue.put( servers[ account ] )		# Store the account dictionary in inQueue. This denotes the data required for a single task: polling a single server

    outQueue = Queue( maxsize = inQueue.qsize() )		# Prepare output queue for storing results

    # Create a number of threads to parallelize the tasks. Threads created using the Worker class inherited from the threading.Thread class:


    workers = [ Worker( pollAccount, inQueue, outQueue ) for ii in range( maxThreads ) ]		# maxThreads is a global variable that determines the maximum number of open threads

    for worker in workers :

        worker.start()		# Begun execution of the thread


    inQueue.join()		# Pause program stepping forward here until all tasks in inQueue are completed


    while not outQueue.empty() :

        yield outQueue.get()		# this wording makes test3() a generator and it should be used as such. test3 will return Buffer type objects from each server poll one at a time.





class Output() :

    '''
    This class stores the information retrieved from each account. It acts as a fancier version of a struct.
    '''

    def __init__( self, settings ) :		# Initialize the account output by storing the account 'settings' dictionary for concurrent use with the lines of output we will be storing

        self.settings = settings	# Store account name in class
        self.emails = []		# Stores the Email objects, one for each email/uid

        self.error = False      # This is a flag used to indicate if an Error has occurred during the construction of this object





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

    try:
        ldt = dt.astimezone( Local )

    except ValueError:

        print('Error - Using .astimezone(local).')
        return ''

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
