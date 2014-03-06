fetchheaders is a python script that uses multiple threads to simultaneously (using multiple threads) access a number of email accounts on imap servers in a secure fashion (using SSL over port 443). The primary purpose of this script is to fetch and display header information; in particular date, from and subject of emails; in the chosen folder in each account (INBOX by default) without having to download entire emails.

Note: This program can only access IMAP servers which allow SSL-based access over port 443.


To set up account access fill in the configuration file ~/.fetchheaders/fetchheaders.conf. One can create multiple configuration files and refer to a particular one using the -c switch when calling the fetchheaders.py script. Run 'fetchheaders.py -h' for details.

Default behaviour is set up in the configuration file.

The configuration behaviour can be over-ridden by passing command-line arguments when the fetchheaders script is called. Run 'fetchheaders -h' to get a list of the command-line arguments. 


If called with the -n switch the program will return only the number of emails in the default folder (number of unseen message and the total number of messages) similar to fetchmail's -c switch.


For more details please read the man page.


Please feel free to email the author of the program if problems arise.


Author: Abid H. Mujtaba
Email: abid.naqvi83@gmail.com

Date: Sep. 24, 1012


## LICENSE

```
Copyright 2012 Abid Hasan Mujtaba

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```