"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia import DefaultAccount, DefaultGuest


class Account(DefaultAccount):
    """
    This class describes the actual OOC account (i.e. the user connecting
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object.

    It can be useful e.g. for storing configuration options for your game, but
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_ACCOUNT_TYPECLASS.


    * available properties

     key (string) - name of account
     name (string)- wrapper for user.username
     aliases (list of strings) - aliases to the object. Will be saved to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     user (User, read-only) - django User authorization object
     obj (Object) - game object controlled by account. 'character' can also be used.
     sessions (list of Sessions) - sessions connected to this account
     is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods

     msg(text=None, **kwargs)
     execute_cmd(raw_string, session=None)
     search(ostring, global_search=False, attribute_name=None, use_nicks=False, location=None, ignore_errors=False, account=False)
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hook methods (when re-implementation, remember methods need to have self as first arg)

     basetype_setup()
     at_account_creation()

     - note that the following hooks are also found on Objects and are
       usually handled on the character level:

     at_init()
     at_cmdset_get(**kwargs)
     at_first_login()
     at_post_login(session=None)
     at_disconnect()
     at_message_receive()
     at_message_send()
     at_server_reload()
     at_server_shutdown()

    """

    pass


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    pass


"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit


class Exit(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """

    pass


"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter


class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    pass


import random

from evennia import DefaultObject, DefaultExit, Command, CmdSet
from evennia.utils import search, delay, dedent
from evennia.prototypes.spawner import spawn

# -------------------------------------------------------------
#
# Object
#
# The Object is the base class for all items
# in Druidia.
#
# Objects may also be "reset". What the reset means
# is up to the object. It can be the resetting of the world
# itself, or the removal of an inventory item from a
# character's inventory when leaving Druidia, for example.
#
# -------------------------------------------------------------

from evennia import DefaultObject


class Object(DefaultObject):
    """
    This is the baseclass for all objects in Druidia.
    """

    def at_object_creation(self):
        """Called when the object is first created."""
        super().at_object_creation()

    def reset(self):
        """Resets the object, whatever that may mean."""
        self.location = self.home


"""

Room typeclasses for Druidia.

This defines special types of Rooms available in Druidia. To keep
everything in one place we define them together with the custom
commands needed to control them. Those commands could also have been
in a separate module (e.g. if they could have been re-used elsewhere.)

"""


from evennia import CmdSet, Command, DefaultRoom
from evennia import utils, create_object, search_object
from evennia import syscmdkeys, default_cmds


# the system error-handling module is defined in the settings. We load the
# given setting here using utils.object_from_module. This way we can use
# it regardless of if we change settings later.
from django.conf import settings

_SEARCH_AT_RESULT = utils.object_from_module(settings.SEARCH_AT_RESULT)

# -------------------------------------------------------------
#
# Room - parent room class.
#
# This room is the parent of all rooms in Druidia.
#
# -------------------------------------------------------------


# for the @detail command we inherit from MuxCommand, since
# we want to make use of MuxCommand's pre-parsing of '=' in the
# argument.
class CmdSetDetail(default_cmds.MuxCommand):
    """
    sets a detail on a room

    Usage:
        @detail <key> = <description>
        @detail <key>;<alias>;... = description

    Example:
        @detail walls = The walls are covered in ...
        @detail castle;ruin;tower = The distant ruin ...

    This sets a "detail" on the object this command is defined on
    (Room in this case). This detail can be accessed with
    the RoomLook command sitting on Room objects (details
    are set as a simple dictionary on the room). This is a Builder command.

    We custom parse the key for the ;-separator in order to create
    multiple aliases to the detail all at once.
    """

    key = "@detail"
    locks = "cmd:perm(Builder)"
    help_category = "World"

    def func(self):
        """
        All this does is to check if the object has
        the set_detail method and uses it.
        """
        if not self.args or not self.rhs:
            self.caller.msg("Usage: @detail key = description")
            return
        if not hasattr(self.obj, "set_detail"):
            self.caller.msg("Details cannot be set on %s." % self.obj)
            return
        for key in self.lhs.split(";"):
            # loop over all aliases, if any (if not, this will just be
            # the one key to loop over)
            self.obj.set_detail(key, self.rhs)
        self.caller.msg("Detail set: '%s': '%s'" % (self.lhs, self.rhs))


class CmdLook(default_cmds.CmdLook):
    """
    looks at the room and on details

    Usage:
        look <obj>
        look <room detail>
        look *<account>

    Observes your location, details at your location or objects
    in your vicinity.

    This is a child of the default Look command, that also
    allows us to look at "details" in the room.  These details are
    things to examine and offers some extra description without
    actually having to be actual database objects. It uses the
    return_detail() hook on Rooms for this.
    """

    # we don't need to specify key/locks etc, this is already
    # set by the parent.
    help_category = "World"

    def func(self):
        """
        Handle the looking. This is a copy of the default look
        code except for adding in the details.
        """
        caller = self.caller
        args = self.args
        if args:
            # we use quiet=True to turn off automatic error reporting.
            # This tells search that we want to handle error messages
            # ourself. This also means the search function will always
            # return a list (with 0, 1 or more elements) rather than
            # result/None.
            looking_at_obj = caller.search(
                args,
                # note: excludes room/room aliases
                candidates=caller.location.contents + caller.contents,
                use_nicks=True,
                quiet=True,
            )
            if len(looking_at_obj) != 1:
                # no target found or more than one target found (multimatch)
                # look for a detail that may match
                detail = self.obj.return_detail(args)
                if detail:
                    self.caller.msg(detail)
                    return
                else:
                    # no detail found, delegate our result to the normal
                    # error message handler.
                    _SEARCH_AT_RESULT(looking_at_obj, caller, args)
                    return
            else:
                # we found a match, extract it from the list and carry on
                # normally with the look handling.
                looking_at_obj = looking_at_obj[0]

        else:
            looking_at_obj = caller.location
            if not looking_at_obj:
                caller.msg("You have no location to look at!")
                return

        if not hasattr(looking_at_obj, "return_appearance"):
            # this is likely due to us having an account instead
            looking_at_obj = looking_at_obj.character
        if not looking_at_obj.access(caller, "view"):
            caller.msg("Could not find '%s'." % args)
            return
        # get object's appearance
        caller.msg(looking_at_obj.return_appearance(caller))
        # the object's at_desc() method.
        looking_at_obj.at_desc(looker=caller)
        return


class CmdGiveUp(default_cmds.MuxCommand):
    """
    Give up the quest and return to Limbo, the start room of the server.
    """

    key = "give up"
    aliases = ["abort"]

    def func(self):
        outro_room = OutroRoom.objects.all()
        if outro_room:
            outro_room = outro_room[0]
        else:
            self.caller.msg(
                "That didn't work (seems like a bug). "
                "Try to use the |wteleport|n command instead."
            )
            return

        self.caller.move_to(outro_room)


class RoomCmdSet(CmdSet):
    """
    Implements the simple room cmdset. This will overload the look
    command in the default CharacterCmdSet since it has a higher
    priority (ChracterCmdSet has priority 0)
    """

    key = "room_cmdset"
    priority = 1

    def at_cmdset_creation(self):
        """add the room commands"""
        self.add(CmdSetDetail())
        self.add(CmdLook())
        self.add(CmdGiveUp())


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.

    This is the base room type for all rooms in Druidia.
    """

    def at_object_creation(self):
        """Called when room is first created"""
        self.cmdset.add_default(RoomCmdSet)

    def at_object_receive(self, new_arrival, source_location):
        """
        When an object enters a room we tell other objects in the room
        about it by trying to call a hook on them. The Mob object uses
        this to cheaply get notified of enemies without having to
        constantly scan for them.

        Args:
            new_arrival (Object): the object that just entered this room.
            source_location (Object): the previous location of new_arrival.

        """
        if new_arrival.has_account and not new_arrival.is_superuser:
            # this is a character
            for obj in self.contents_get(exclude=new_arrival):
                if hasattr(obj, "at_new_arrival"):
                    obj.at_new_arrival(new_arrival)

    def return_detail(self, detailkey):
        """
        This looks for an Attribute "obj_details" and possibly
        returns the value of it.

        Args:
            detailkey (str): The detail being looked at. This is
                case-insensitive.

        """
        details = self.db.details
        if details:
            return details.get(detailkey.lower(), None)

    def set_detail(self, detailkey, description):
        """
        This sets a new detail, using an Attribute "details".

        Args:
            detailkey (str): The detail identifier to add (for
                aliases you need to add multiple keys to the
                same description). Case-insensitive.
            description (str): The text to return when looking
                at the given detailkey.

        """
        if self.db.details:
            self.db.details[detailkey.lower()] = description
        else:
            self.db.details = {detailkey.lower(): description}


"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from evennia import DefaultScript


class Script(DefaultScript):
    """
    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.

    """

    pass
