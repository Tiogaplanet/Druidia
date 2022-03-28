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

CONNECTION_SCREENA = """
|b================================================================================|n


  |g________                  .__     .___.__         
  \______ \  _______  __ __ ||__|  __| _/||__||_____   
   |    |  \ \_  __ \|  |  \|  | / __ | |  |\__  \  
   |    `   \ |  | \/|  |  /|  ||/ /_/ | |  | / __ \_
  /_______  / ||__|   ||____/ ||__||\____ | ||__|(____  /
          \/                         \/          \/|n
  

  |yLet's set a course for Druidia.  -Lone Starr|n




     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""

CONNECTION_SCREENB = """
|b================================================================================|n


  |r________                  .__     .___.__         
  \______ \  _______  __ __ ||__|  __| _/||__||_____   
   |    |  \ \_  __ \|  |  \|  | / __ | |  |\__  \  
   |    `   \ |  | \/|  |  /|  ||/ /_/ | |  | / __ \_
  /_______  / ||__|   ||____/ ||__||\____ | ||__|(____  /
          \/                         \/          \/|n

  
  |yNever underestimate the power of the Schwartz!  -Yogurt|n




     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""

CONNECTION_SCREENC = """
|b================================================================================|n


  |c________                  .__     .___.__         
  \______ \  _______  __ __ ||__|  __| _/||__||_____   
   |    |  \ \_  __ \|  |  \|  | / __ | |  |\__  \  
   |    `   \ |  | \/|  |  /|  ||/ /_/ | |  | / __ \_
  /_______  / ||__|   ||____/ ||__||\____ | ||__|(____  /
          \/                         \/          \/|n

  
  |yWhen does this happen in the movie?  -Dark Helmet|n




     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""

CONNECTION_SCREEND = """
|b================================================================================|n


  |m________                  .__     .___.__         
  \______ \  _______  __ __ ||__|  __| _/||__||_____   
   |    |  \ \_  __ \|  |  \|  | / __ | |  |\__  \  
   |    `   \ |  | \/|  |  /|  ||/ /_/ | |  | / __ \_
  /_______  / ||__|   ||____/ ||__||\____ | ||__|(____  /
          \/                         \/          \/|n

  
  |yWe can't stop, it's too dangerous! We have to slow down first!
                                                         -Colonel Sandurz|n



     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""
