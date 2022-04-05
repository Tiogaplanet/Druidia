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
|=mdrop grenade|n         |=mnw|n                |=mn|n                 |=mne|n          |=mshift panel|n
|=mlanguages|n                                                              |=minventory|n
|=mwhisper|n                                                                  |=mccreate|n
|=msay hi|n                                                                    |=maccess|n
|=mstyle|n                                                                      |=mcboot|n
|=mlook|n           |g________                  .__     .___.__                    |=mpage|n
|=mwho|n            |g\______ \  _______  __ __ ||__|  __| _/||__||_____               |=ml e|n
|=mnw|n              |g|    |  \ \_  __ \|  |  \|  | / __ | |  |\__  \               |=mne|n
|=mw|n               |g|   _|   \ |  | \/|  |  /|  ||/ /_/ | |  | / __ \_              |=me|n
|=mw|n              |g/_______  / ||__|   ||____/ ||__||\____ | ||__|(____  /              |=me|n
|=msw|n                     |g\/                         \/          \/|n              |=mse|n
|=mdig|n                                                                          |=mooc|n
|=mhelp|n                                                                        |=mtime|n
|=moption|n           |yLet's set a course for Druidia.  -Lone Starr|n              |=mcemit|n
|=mccreate|n                                                                   |=msetdes|n
|=mshutdown|n                                                                |=mchannels|n
|=mtel limbo|n                                                              |=minventory|n
|=mlook south|n            |=msw|n               |=ms|n                 |=mse|n          |=mpush button|n
     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""

CONNECTION_SCREENB = """
|b================================================================================|n
|=mdrop grenade|n         |=mne|n                |=mn|n                 |=mnw|n          |=mshift panel|n
|=mlanguages|n                                                              |=minventory|n
|=mevennia|n                                                                  |=mccreate|n
|=msay hi|n                                                                    |=maccess|n
|=mstyle|n                                                                      |=mcboot|n
|=mlook|n           |r________                  .__     .___.__                    |=mpage|n
|=mwho|n            |r\______ \  _______  __ __ ||__|  __| _/||__||_____               |=ml w|n
|=mne|n              |r|    |  \ \_  __ \|  |  \|  | / __ | |  |\__  \               |=mnw|n
|=me|n               |r|   _|   \ |  | \/|  |  /|  ||/ /_/ | |  | / __ \_              |=mw|n
|=me|n              |r/_______  / ||__|   ||____/ ||__||\____ | ||__|(____  /              |=mw|n
|=mse|n                     |r\/                         \/          \/|n              |=msw|n
|=mdig|n                                                                          |=mooc|n
|=mhelp|n                                                                        |=mtime|n
|=moption|n     |yGo then.  There are other worlds than these. -Jake Chambers|n     |=mcemit|n
|=mccreate|n                                                                  |=msetdesc|n
|=mshutdown|n                                                                |=mchannels|n
|=mtel limbo|n                                                              |=minventory|n
|=mlook north|n           |=mse|n                |=ms|n                 |=msw|n          |=mpush button|n
     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""

CONNECTION_SCREENC = """
|b================================================================================|n
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|r////////////////////////////////////////////////////////////////////////////////|n
|y////////////////////////////////////////////////////////////////////////////////|n
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B/|c________|B/|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y/|c.__|B/|b/|B//|y/|c.___.__|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B/|c\______ \|y//|c_______|y/|r/|c__ __ ||__|||b/|B/|c__| _/||__||_____|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|c|    |  \ \_  __ \|  |  \|  |||b/|c/ __ |||B/|c|  |\__  \|B/|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|r////////////////|c|   _|   \ |  | \/|  |  /|  ||/ /_/ |||B/|c|  | / __ \_|r///////////////
|y///////////////|c/_______  /|r/|c||__|||B/|y//|c||____/|y/|c||__||\____ |||B/|c||__|(____  /|y///////////////
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B/|c\/|y/|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|c\/|B//|y//|r//|B/|b/|B//|c\/|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|r//////////////////////////|yThey've gone to plaid. -Barf|r//////////////////////////|n
|y////////////////////////////////////////////////////////////////////////////////|n
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//
|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|y//|r//|B/|b/|B//|n
     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""

CONNECTION_SCREEND = """
|b================================================================================|n
                                                            .
      .                       .       .
                .                                  .

               |m________                  .__     .___.__         
               \______ \  _______  __ __ ||__|  __| _/||__||_____   
      |n.         |m|    |  \ \_  __ \|  |  \|  | / __ | |  |\__  \            |n.
                |m|   _|   \ |  | \/|  |  /|  ||/ /_/ | |  | / __ \_
               /_______  / ||__|   ||____/ ||__||\____ | ||__|(____  /         |n.
                       |m\/                         \/          \/|n
              .
  .                   .                 .                               .
   .
             |yNever underestimate the power of the Schwartz!  -Yogurt|n  
                  .                                        .
.                           .              .                               .
             .
                                                                 .
     Connect to your account                          Create an account
  |wconnect <username> <password>|n                 |wcreate <username> <password>|n
           Enter |whelp|n for more info | Enter |wlook|n to show this screen
|b================================================================================|n"""
