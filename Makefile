# Copyright 2012 Abid Hasan Mujtaba
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Author: Abid H. Mujtaba
# Date: Sep. 30, 2012


# The location of the 'fetchheaders' binary. Ideally this should be a folder in the system path. Using the default value of '/usr/local/bin' means 'make install' will need to be executed as root.
# Change this value if you want the binary (actually symbolic link) placed somewhere else.

BIN_LOCATION=/usr/local/bin

# All of the files of the package will be stored in PACKAGE_LOCATION, which will be created if required. The binary will be a symbolic link to $PACKAGE_LOCATION/fetchheaders.py

PACKAGE_LOCATION=/usr/local/share/fetchheaders

# Change the value of CREATE_MANPAGE to zero (0) if you don't want to install a manpage.

CREATE_MANPAGE=1

# A list of all the files in the application. These are the files that 'make' moves about

scripts = fetchheaders.py miscClasses.py imapServer.py urwidDisplay.py

config = fetchheaders.conf

spec = fetchheaders.conf.spec

manFiles = fetchheaders.1.gz



.PHONY: install uninstall purge config help

install:

	@echo -e "\nInstalling the application files. This command needs to be run as root (perhaps using sudo) since it installs files in /usr/local/share/ and /usr/local/bin/. Run 'make config' to install the configuration file if installing 'fetchheaders' for first time or if you need to over-write the existing configuration file with the default copy.\n"
	
# Check if ~/.fetchheaders folder exists. If not create it :

	@if [ ! -d $(PACKAGE_LOCATION) ]; then \
	\
		mkdir $(PACKAGE_LOCATION) ; \
		echo -e "mkdir $(PACKAGE_LOCATION)\n" ; \
	fi

# Copy .py scripts and spec file to PACKAGE_LOCATION :

	@for file in $(scripts) $(spec); do \
	\
		cp $$file $(PACKAGE_LOCATION) ; \
		echo "cp $$file $(PACKAGE_LOCATION)" ; \
	done

## Check if configuration file exists. If not copy it.
#
#	@echo -e "\nChecking if configuration file existis and copying it if it does NOT.\n"
#
#	@if [ ! -f ~/.fetchheaders.conf ]; then \
#	\
#		cp fetchheaders.conf ~/ ; \
#	\
#	fi ;

ifeq ($(CREATE_MANPAGE),1)

	@cp fetchheaders.1.gz /usr/share/man/man1/

endif

# Check if it exists and if not, create symbolic link to the fetchheaders main script

	@if [ ! -f $(BIN_LOCATION)/fetchheaders ]; then \
	\
		ln -s $(PACKAGE_LOCATION)/fetchheaders.py $(BIN_LOCATION)/fetchheaders ; \
		echo -e "\nln -s $(PACKAGE_LOCATION)/fetchheaders.py $(BIN_LOCATION)/fetchheaders" ; \
	\
	fi ;




config:

# Installs the configuration file, possibly over-writing the one that already exists.
	
	@echo -e "\nInstalling (and possibly over-writing) configuration file.\n"

	@cp fetchheaders.conf ~/.fetchheaders.conf

	@echo "cp fetchheaders.conf ~/.fetchheaders.conf"



# Note how we used the phony target 'uninstall' as a prerequisite for the phony target 'purge'. This means that after the rules for 'purge' are executed it does the same for 'uninstall' treating it as a sub-routine. A property of phony targets.

purge: uninstall

# Remove the configuration files and then run the "uninstall" recipe

	@echo -e "\nRemoving configuration file.\n"
	
	-rm ~/.fetchheaders.conf



uninstall:

	@echo -e "\nRemoving the fetchheaders scripts and manpage but NOT the configuration file UNLESS 'make purge' has been issued.\n"

# Removing entire pakcage folder:

	-rm -r $(PACKAGE_LOCATION)

	@echo -e "rm -r $(PACKAGE_LOCATION))"


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
	@echo -e "\n\tinstall - Installs the applications scripts and the configuration files unless the configuration files already exist in which case it DOES not over-write them. Run as root."
	@echo -e "\n\tuninstall - Remove application scripts, binary and manpage. Leave the configuration files. Run as root."
	@echo -e "\n\tpurge - Remove ALL application files and folders including the configuration file. Run as root."
	@echo -e "\n\tconfig - Install the configuration file, over-writing existing one. Use to create clean configuration file."
