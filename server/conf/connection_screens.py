# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils

CONNECTION_SCREEN = """
|b==============================================================|n
 Welcome to |g{}|n, powered by Evennia version {}!

|g{}|n is set in a dystopian future, in which people live in 
massive apartment complexes, large enough to be entire cities 
in their own right.  Violent gangs and drug dealers shakedown 
locals regularly. Meanwhile, the Global Economic Consortium 
ignores the poverty and crime in its pursuit of intergalactic 
wealth and respect among newly discovered races.  But that is
a story thousands of miles above this meager existence.

 Connect to your account by typing (without the <>):
      |wconnect <username> <password>|n
 If you need to create an account, type:
      |wcreate <username> <password>|n

 Enter |whelp|n for more info. |wlook|n will re-show this screen.
|b==============================================================|n""".format(
    settings.SERVERNAME, utils.get_evennia_version("short"), settings.SERVERNAME
)
