# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Feb 8, 2017 4:11:17 PM$"

import os
import getpass


#: key directory
KEY_DIR = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], 'key')
#: Gsheet permission scope
SCOPES = "https://www.googleapis.com/auth/spreadsheets"
#: Application name
APPLICATION_NAME = "Android Test Framework Spreadsheet API ({})".format(getpass.getuser())
#: Google service timeout in seconds
SERVICE_TIMEOUT = 300
#: Values limit for one update request
UPDATE_REQUEST_LIMIT = 300
