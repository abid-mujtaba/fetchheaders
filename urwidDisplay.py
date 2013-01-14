#!/usr/bin/python
#
# Copyright (c) 2012 Abid Hasan Mujtaba
# See the file LICENSE for copying permission.
#
# Author: Abid H. Mujtaba
# Email: abid.naqvi83@gmail.com
#
# Start Date: Jan. 13, 2013
# Last Revised: Jan. 13, 2013
#
# This script implements a urwid based class that will be used to display the email header information. The display will allow for mutt-style navigation (using j/k keys) and enable the user to mark messages for deletion. 

class urwidDisplay() :

	'''
	This class acts as a wrapper around urwid objects and in fact will contian the urwid Main Loop as well. Most of the active parts will be carried out in the __init__ method so that the very act of creating an object of this class will cause the email header display using urwid to be executed. We will remain the __init__ method until the loop ends at which point the program will terminate as well. To that end the urwid event handler functions will be members of this class as well.
	'''

	def __init__( self, servers, settings ) :

		'''
		This is the actionable part of the class and is responsible for initializing the class objects, implementing the urwid display and executing the main loop. 'servers' is an object which contains all the necessary information for logging in to the email accounts and extracting headers.

		maxThreads: Max. number of simulatneous threads that the program is allowed to open. A global setting.
		'''

		# Import the necessary modules and functions:

		import urwid
		from miscClasses import threadedExec		# This function implements email account access using threads


		self.settings = settings		# Store the settings (mostly global for the program) locally in a dictionary


		# Define the palette that will be used by urwid. Note that is defined to be a member of the urwidDisplay class as all objects will be

		normal_bg_color = 'black'		# Here we define the default normal and focus state bg colors for the header lines displayed
		focus_bg_color = 'light blue'

		self.palette = [
			( 'title', 'yellow', 'dark blue' ),

			( 'account', 'light red', normal_bg_color ),
			( 'bw', 'white', normal_bg_color ),
			
			( 'flag', 'dark green', normal_bg_color ),	# We define the normal state color scheme for the various parts of the header
			( 'date', 'brown', normal_bg_color ),
			( 'from', 'dark cyan', normal_bg_color ),
			( 'subject', 'dark green', normal_bg_color ),
			( 'subjectSeen', 'brown', normal_bg_color ),
									# We define the 'focus' state color scheme for various parts of the header. Note the 'F_' at the beginning of each name
			( 'F_bw', 'white', focus_bg_color ) ,		# Black and White text when focussed
			( 'F_flag', 'light green', focus_bg_color ),	
			( 'F_date', 'yellow', focus_bg_color ),
			( 'F_from', 'light cyan', focus_bg_color ),
			( 'F_subject', 'light green', focus_bg_color ),
			( 'F_subjectSeen', 'yellow', focus_bg_color ), 	
									# We define the normal state flagged for Deletion scheme for the header. Note the 'D_' at the beginning of each name
			( 'D_bw', 'dark red', normal_bg_color ),
			( 'D_flag', 'dark red', normal_bg_color ),
			( 'D_date', 'dark red', normal_bg_color ),
			( 'D_from', 'dark red', normal_bg_color ),
			( 'D_subject', 'dark red', normal_bg_color ),
			( 'D_subjectSeen', 'dark red', normal_bg_color ),
									# We define the focus state flagged for Deletion scheme for the header. Note the 'DF_' at the beginning of each name.
			( 'DF_bw', 'dark red', focus_bg_color ),
			( 'DF_flag', 'dark red', focus_bg_color ),
			( 'DF_date', 'dark red', focus_bg_color ),
			( 'DF_from', 'dark red', focus_bg_color ),
			( 'DF_subject', 'dark red', focus_bg_color ),
			( 'DF_subjectSeen', 'dark red', focus_bg_color ) ]	



		self.title = urwid.AttrMap( urwid.Text( " FetchHeaders      q: Quit    a: Abort    d: Delete    u: UnDelete    j: Down    k: Up" ), 'title' )

		self.div = urwid.Divider()

		self.titlePile = urwid.Pile( [ self.title, self.div ] )


		self.emails = []		# This is a list which will contain the emails whose headers have been displayed. We will use it when shifting focus and marking for deletion.

		self.focus = -1			# Initially no header has focus. This is donated by the value -1. 0 will donate the first header corresponding to self.emails[0].

		
		self.List = []		# This is the list of objects that will be used to construct the main listbox that displays all email headers and auxiliary information. 

		# We will now extract header information from each account and use it to construct various objects. While doing so we must keep in mind that when focus shifts the objects must be re-drawn explicitly. This can be handled by constructing the lines every time it is required, using separate functions to handle the construction by simply passing them the same information
		

		for out in threadedExec( servers, self.settings[ 'maxThreads' ] ) :		# This calls the threaded processed to extract information and return it in an iterable queue

			# Construct account line widget
	
			account = urwid.Text( ( 'account', ' ' + out.settings[ 'name' ] + ':' ) )
	
			if out.settings[ 'showNums' ] :			# Numbers are supposed to displayed after the account name
	
				numbers = urwid.Text( ( 'bw', '( total: ' + str( out.numAll ) + ' | unseen: ' + str( out.numUnseen ) + ' )' ) ) 
	
				accountLine = urwid.Columns( [ ( 'fixed', 13, account ), numbers ] )
	
			else :			# Don't display numbers
	
				accountLine = urwid.Columns( [ ( 'fixed', 13, account ) ] )
	
	
			self.List += [ accountLine, self.div ]		# First line displays account name and number of messages



			# We now construct and display the email headers
	
			for ii in range( len( out.emails ) ) :
	
				email = out.emails[ ii ]

				email.account = out.settings[ 'name' ]		# Store name of account associated with each email

				email.Delete = False		# Boolean Flag for tracking if email has to be deleted.

				email.serial = ii + 1		# Serial Number associated with this email

				email.numDigits = out.numDigits		# No. of digits for displaying serial number, calculated by analyzing the number of emails for this particular account

				email.listPos = len( self.List )	# Store the position of the email header urwid object (urwid.Columns) in self.List. Will need it for focusing or deletion.

				self.emails.append( email )		# Add the displayed email to the self.emails list


				line = self.constructLine( email, focus = False )


				self.List.append( line )		# Call constructLine to create header line using data in 'email' object. ii + 1 is serial number



			self.List += [ self.div, self.div ] 		# Add two empty lines after account ends


		self.total = len( self.emails )		# Total no. of emails being displayed


		# All account information has been input and the urwid display is almost ready:

		self.listbox = urwid.ListBox( self.List )

		self.frame = urwid.Frame( self.listbox, header = self.titlePile )		# By using a frame we ensure that the top title doesn't move when we scroll through the listbox
		
		self.loop = urwid.MainLoop( self.frame, self.palette, unhandled_input = self.handler )

		
		# Now we run the main loop:

		self.loop.run()

	


	def handler( self, key ) :

		'''
		This is the input handler. This takes unprocessed key presses from urwid and translates them in to the appropriate action.
		'''

		import urwid


		if key in ( 'a', 'A' ) :		# Exit loop without making any changes (NO Deletions) when the 'A' key is pressed (in any case) 

			raise urwid.ExitMainLoop()


		if key in ( 'j', 'J' ) :		# This pushes focus down

			self.focus += 1

			self.shiftFocus( self.focus - 1 )		# Call the shiftFocus() method to implement the change in focus. We need to pass it the last focus so that it can be unfocussed.


		if key in ( 'k', 'K' ) :		# This pushes the focus up

			self.focus -= 1

			self.shiftFocus( self.focus + 1 )


		if key in ( 'd', 'D' ) :		# Email in focus must be flagged for deletion

			self.emails[ self.focus ].Delete = True		# Set Delete flag on focused email

			self.shiftFocus( None )		# Call shiftFocus() to implement change in display status. 'None' is passed since the focus hasn't moved.


		if key in ( 'u', 'U' ) :

			self.emails[ self.focus ].Delete = False	# UnSet Delete flag on focused email

			self.shiftFocus( None )


		if key in ( 'q', 'Q' ) :

			self.quit()		# Call the quit() method/function to delete flagged emails and exit the program



	
	def quit( self ) :

		'''
		This method/function deletes all emails that have been flagged for deletion and then exits the program.
		'''

#		fout = open( 'output.txt', 'w' )

		# The first step is to scan self.emails and find the emails flagged for deletion. We collect them in a single data structure:

		delete = {}

		for email in self.emails :

			if email.Delete :		# Email is marked for deletion

				if not email.account in delete.keys() :		# Checking if the account exists in the 'delete' dictionary as a key. If not it must be created as an empty list

					delete[ email.account ] = []		# Empty list created to hold uids of emails flagged for deletion

				delete[ email.account ].append( email.uid )


#				fout.write( email.account + '   ' + email.uid + '    ' + email.Date + '  ' + email.From + '  ' + email.Subject + '\n' )

#		fout.write( '\n\n' )
#		fout.write( str( delete ) )
#
#		fout.close()


		import urwid

		raise urwid.ExitMainLoop()




	def shiftFocus( self, oldFocus ) :

		'''
		This method/function is called whenever the focus shifts. It implements said change.
		'''

		# The first step is to check whether the focus is out of bounds or not.

		if self.focus < 0 :  self.focus = self.total - 1		# Treat emails in a circular data structure. We set focus to the last email.

		if self.focus >= self.total :  self.focus = 0			# Move around the circle and set focus to first email.


		# First we unfocus the previously focussed email, if there is one.

		if oldFocus != None :		# If 'None' has been passed in the focus hasn't changed position, for instance if the email is to be marked for deletion.

			email = self.emails[ oldFocus ]
	
			self.List[ email.listPos ] = self.constructLine( email, focus = False )
	

		# Now implement change in focus.

		email = self.emails[ self.focus ]		# We select the email object associated with the new focus

		self.List[ email.listPos ] = self.constructLine( email, focus = True )


		# Finally change listbox focus so that the listbox scrolls properly with our scrolling:

		self.listbox.set_focus( email.listPos )





	def constructLine( self, email, focus = False ) :

		'''
		This function takes the 'email' object and a single flag and uses them to construct a urwid.Column object representing the correctly formatted header line for the display. This is stored in the listbox for displaying.

		serialNum: An integer specifying the serial number associated with the email in the list of emails when it is displayed.
		
		numDigits: Number of digits for displaying the serial number. An account level value that has already been calculated.

		self.settings: A Dictionary containing the following settings.
	
			showUnseen: A boolean flag. Global setting. When true indicates that only unseen messages are to be displayed.
	
			showFlags: A boolean flag. Gobal setting. When true indicates the flags are to displayed

		focus: A boolean flag. When True indicates that the line is in focus and so the coloring scheme needs to be changed.
		'''

		import urwid
		from miscClasses import strWidth as sW
		
		if focus : pre = 'F_'		# This string determines which color from the palette is used: normal of focus scheme, flagged for deletion or not.

		else : pre = ''

		if email.Delete :

			if focus: pre = 'DF_'		# Email is both flagged for deletion and in focus

			else : pre = 'D_'		# Email is flagged for deletion


		date = urwid.Text( ( pre + 'date', sW( email.Date, 17 ) ) )
		From = urwid.Text( ( pre + 'from', sW( email.From, 30 ) ) )
		serial = urwid.Text( ( pre + 'bw', sW( str( email.serial ), email.numDigits, align = '>' ) ) ) 
		

		if not email.Seen :		# If email is unseen then:

			subject = urwid.Text( ( pre + 'subject', sW( email.Subject, 120 ) ) )
		
		else:

			subject = urwid.Text( ( pre + 'subjectSeen', sW( email.Subject, 120 ) ) )


		if self.settings[ 'showFlags' ] :		# Flags are to be displayed

			if email.Seen :

				if email.Delete : ch = " D "

				else : ch = "   "

			else :
				if email.Delete : ch = " ND"

				else : ch = " N "


			sep = [ ('fixed', 2, urwid.Text(( pre + 'bw', " [" ))), ('fixed', 3, urwid.Text(( pre + 'flag', ch ))), ('fixed', 4, urwid.Text(( pre + 'bw', "]   " ))) ] 
		
		else :
			sep = [ ( 'fixed', 3, urwid.Text(( pre + 'bw', ".  " )) ) ]


		lineList = [ ('fixed', email.numDigits, serial) ] + sep + [ ('fixed', 21, date ), ('fixed', 34, From), subject ]

		
		line = urwid.AttrMap( urwid.Columns( lineList ), pre + 'bw' )		# Applying the AttrMap here ensures the whole line gets the same background color

		return line		# Return the constructed line
