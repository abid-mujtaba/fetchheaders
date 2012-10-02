# Author: Abid H. Mujtaba
# Date: Sep. 30, 2012
#
# Copyright (c) 2012 Abid Hasan Mujtaba
# See the file LICENSE for copying permission.


# The location of the 'fetchheaders' binary. Ideally this should be a folder in the system path. Using the default value of '/usr/local/bin' means 'make install' will need to be executed as root.
# Change this value if you want the binary (actually symbolic link) placed somewhere else.

BIN_LOCATION=/usr/local/bin

# Change the value of CREATE_MANPAGE to zero (0) if you don't want to install a manpage.

CREATE_MANPAGE=1

# A list of all the files in the application. These are the files that 'make' moves about

scripts = fetchheaders.py miscClasses.py imapServer.py

configs = fetchheaders.conf fetchheaders.conf.spec

manFiles = fetchheaders.1.gz



.PHONY: install uninstall purge config install_binary help

install:

	@echo -e "\nInstalling the application files. Run 'make install_binary' to install the binary and manpage. Run 'make help' for a list of options.\n"
	
# Check if ~/.fetchheaders folder exists. If not create it :

	@if [ ! -d ~/.fetchheaders ]; then \
	\
		mkdir ~/.fetchheaders ; \
		echo -e "mkdir ~/.fetchheaders\n" ; \
	fi

# Copy .py scripts to ~/.fetchheaders :

	@for file in $(scripts); do \
	\
		cp $$file ~/.fetchheaders/ ; \
		echo "cp $$file ~/.fetchheaders/" ; \
	done

# Check if configuration and specificiation files exist. If not copy them.

	@echo -e "\nChecking if configuration files exist and copying them if they do NOT.\n"

	@for file in $(configs); do \
	\
		if [ ! -f ~/.fetchheaders/$$file ]; then \
		\
			cp $$file ~/.fetchheaders/ ; \
		\
			echo "cp $$file ~/.fetchheaders/" ; \
		fi ; \
	done




install_binary:

	@echo -e "\nInstalling the binary to $(BIN_LOCATION) and the manpage to /usr/share/man/man1/. Should be run as root.\n"

# Copy manpage if the CREATE_MANPAGE flag is equal to 1. This process will require root access since it accesses the /usr/... folder tree:
	
ifeq ($(CREATE_MANPAGE),1)

	@cp fetchheaders.1.gz /usr/share/man/man1/
	
	@echo -e "\ncp fetchheaders.1.gz /usr/share/man/man1/"
endif

# Create symbolic link to the fetchheaders main script

	@ln -s ~/.fetchheaders/fetchheaders.py $(BIN_LOCATION)/fetchheaders

	@echo -e "\nln -s ~/.fetchheaders/fetchheaders.py $(BIN_LOCATION)/fetchheaders"




config:

# Installs the configuration and specification file, possibly over-writing ones that already exist.
	
	@echo -e "\nInstalling (and possibly over-writing) configuration files.\n"

	@for file in $(configs); do \
	\
		cp $$file ~/.fetchheaders/ ; \
	\
		echo "cp $$file ~/.fetchheaders/" ; \
	done
	
	# Use a for loop here



# Note how we used the phony target 'uninstall' as a prerequisite for the phony target 'purge'. This means that after the rules for 'purge' are executed it does the same for 'uninstall' treating it as a sub-routine. A property of phony targets.

purge: uninstall

# Remove the configuration files and then run the "uninstall" recipe

	@echo -e "\nRemoving configuration files.\n"

	@-for file in $(configs); do \
	\
		rm ~/.fetchheaders/$$file ; \
	\
		echo "rm ~/.fetchheaders/$$file" \
	done




uninstall:

	@echo -e "\nRemoving the fetchheaders scripts and manpage but NOT the configuration files (run 'make purge' to remove configuration files as well).\n"

# Removing 'fetchheaders' scripts but not configuration files

	@-for file in $(scripts); do \
	\
		rm ~/.fetchheaders/$$file ; \
	\
		echo "rm ~/.fetchheaders/$$file" ; \
	done

# Removing compile python files *.pyc

	-rm ~/.fetchheaders/*.pyc

	@echo "rm ~/.fetchheaders/*.pyc"


# Removing 'fetchheaders' symoblic link, requires root access.

	@echo -e "rm $(BIN_LOCATION)/fetchheaders\n"

	-rm $(BIN_LOCATION)/fetchheaders


# Remove fetchheaders manpage if the configuration flag indicates that it has been installed in the first place.

ifeq ($(CREATE_MANPAGE),1)

	@echo -e "rm /usr/share/man/man1/fetchheaders.1.gz\n"

	-rm /usr/share/man/man1/fetchheaders.1.gz
	
endif



help:

	@echo -e "\nOptions:" 
	@echo -e "\n\tinstall - Installs the applications scripts and the configuration files unless the configuration files already exist in which case it DOES not over-write them."
	@echo -e "\n\tinstall_binary Installs the fetchheaders binary to BIN_LOCATION and the manpage to /usr/share/man/man1/. Should be run as root."
	@echo -e "\n\tuninstall - Remove application scripts, binary and manpage. Leave the configuration files. Run as root if you wish to remove the binary and manpage."
	@echo -e "\n\tpurge - Remove ALL application files and folders including the configuration files. Run as root if you wish to remove the binary and mangpage."
	@echo -e "\n\tconfig - Install the configuration and specification files, over-writing existing ones. Use to create clean configuration and specification files."
