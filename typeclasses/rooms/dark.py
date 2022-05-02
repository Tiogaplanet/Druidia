# -------------------------------------------------------------------------------
#
# Dark Room - a room with states
#
# This room limits the movemenets of its denizens unless they carry an active
# LightSource object (LightSource is defined in
#                                       world.objects.LightSource)
#
# -------------------------------------------------------------------------------


import random
from evennia import TICKER_HANDLER
from evennia import CmdSet, Command
from evennia import utils, create_object, search_object
from evennia import syscmdkeys, default_cmds

from typeclasses.room import Room
from typeclasses.widgets.lights import LightSource


DARK_MESSAGES = (
    "It is pitch black. You are likely to be eaten by a grue.",
    "It's pitch black. You fumble around but cannot find anything.",
    "You don't see a thing. You feel around, managing to bump your fingers hard against something. Ouch!",
    "You don't see a thing! Blindly grasping the air around you, you find nothing.",
    "It's totally dark here. You almost stumble over some un-evenness in the ground.",
    "You are completely blind. For a moment you think you hear someone breathing nearby ... "
    "\n ... surely you must be mistaken.",
    "Blind, you think you find some sort of object on the ground, but it turns out to be just a stone.",
    "Blind, you bump into a wall. The wall seems to be covered with some sort of vegetation,"
    " but its too damp to burn.",
    "You can't see anything, but the air is damp. It feels like you are far underground.",
)

ALREADY_LIGHTSOURCE = (
    "You don't want to stumble around in blindness anymore. You already "
    "found what you need. Let's get light already!")

FOUND_LIGHTSOURCE = (
    "Your fingers bump against a splinter of wood in a corner."
    " It smells of resin and seems dry enough to burn! "
    "You pick it up, holding it firmly. Now you just need to"
    " |wlight|n it using the flint and steel you carry with you.")


class CmdLookDark(Command):
    """
    Look around in darkness

    Usage:
      look

    Look around in the darkness, trying
    to find something.
    """

    key = "look"
    aliases = ["l", "feel", "search", "feel around", "fiddle"]
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """
        Implement the command.

        This works both as a look and a search command; there is a
        random chance of eventually finding a light source.
        """
        caller = self.caller

        # count how many searches we've done
        nr_searches = caller.ndb.dark_searches
        if nr_searches is None:
            nr_searches = 0
            caller.ndb.dark_searches = nr_searches

        if nr_searches < 4 and random.random() < 0.90:
            # we don't find anything
            caller.msg(random.choice(DARK_MESSAGES))
            caller.ndb.dark_searches += 1
        else:
            # we could have found something!
            if any(obj for obj in caller.contents
                   if utils.inherits_from(obj, LightSource)):
                #  we already carry a LightSource object.
                caller.msg(ALREADY_LIGHTSOURCE)
            else:
                # don't have a light source, create a new one.
                create_object(LightSource, key="splinter", location=caller)
                caller.msg(FOUND_LIGHTSOURCE)


class CmdDarkHelp(Command):
    """
    Help command for the dark state.
    """

    key = "help"
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """
        Replace the the help command with a not-so-useful help
        """
        string = (
            "Can't help you until you find some light! Try looking/feeling around for something to burn. "
            "You shouldn't give up even if you don't find anything right away."
        )
        self.caller.msg(string)


class CmdDarkNoMatch(Command):
    """
    This is a system command. Commands with special keys are used to
    override special sitations in the game. The CMD_NOMATCH is used
    when the given command is not found in the current command set (it
    replaces Evennia's default behavior or offering command
    suggestions)
    """

    key = syscmdkeys.CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        """Implements the command."""
        self.caller.msg(
            "Until you find some light, there's not much you can do. "
            "Try feeling around, maybe you'll find something helpful!")


class DarkCmdSet(CmdSet):
    """
    Groups the commands of the dark room together.  We also import the
    default say command here so that players can still talk in the
    darkness.

    We give the cmdset the mergetype "Replace" to make sure it
    completely replaces whichever command set it is merged onto
    (usually the default cmdset)
    """

    key = "darkroom_cmdset"
    mergetype = "Replace"
    priority = 2

    def at_cmdset_creation(self):
        """populate the cmdset."""
        self.add(CmdLookDark())
        self.add(CmdDarkHelp())
        self.add(CmdDarkNoMatch())
        self.add(default_cmds.CmdSay())
        self.add(default_cmds.CmdQuit())
        self.add(default_cmds.CmdHome())


class DarkRoom(Room):
    """
    A dark room. This tries to start the DarkState script on all
    objects entering. The script is responsible for making sure it is
    valid (that is, that there is no light source shining in the room).

    The is_lit Attribute is used to define if the room is currently lit
    or not, so as to properly echo state changes.

    Since this room is meant as a sort of catch-all, we also make sure 
    to heal characters ending up here.
    """

    def at_object_creation(self):
        """
        Called when object is first created.
        """
        super().at_object_creation()
        # the room starts dark.
        self.db.is_lit = False
        self.cmdset.add(DarkCmdSet, permanent=True)

    def at_init(self):
        """
        Called when room is first recached (such as after a reload)
        """
        self.check_light_state()

    def _carries_light(self, obj):
        """
        Checks if the given object carries anything that gives light.

        Note that we do NOT look for a specific LightSource typeclass,
        but for the Attribute is_giving_light - this makes it easy to
        later add other types of light-giving items. We also accept
        if there is a light-giving object in the room overall (like if
        a splinter was dropped in the room)
        """
        return (obj.is_superuser or obj.db.is_giving_light
                or any(o for o in obj.contents if o.db.is_giving_light))

    def _heal(self, character):
        """
        Heal a character.
        """
        health = character.db.health_max or 20
        character.db.health = health

    def check_light_state(self, exclude=None):
        """
        This method checks if there are any light sources in the room.
        If there isn't it makes sure to add the dark cmdset to all
        characters in the room. It is called whenever characters enter
        the room and also by the Light sources when they turn on.

        Args:
            exclude (Object): An object to not include in the light check.
        """
        if any(
                self._carries_light(obj) for obj in self.contents
                if obj != exclude):
            self.locks.add("view:all()")
            self.cmdset.remove(DarkCmdSet)
            self.db.is_lit = True
            for char in (obj for obj in self.contents if obj.has_account):
                # this won't do anything if it is already removed
                char.msg("The room is lit up.")
        else:
            # noone is carrying light - darken the room
            self.db.is_lit = False
            self.locks.add("view:false()")
            self.cmdset.add(DarkCmdSet, permanent=True)
            for char in (obj for obj in self.contents if obj.has_account):
                if char.is_superuser:
                    char.msg(
                        "You are Superuser, so you are not affected by the dark state."
                    )
                else:
                    # put players in darkness
                    char.msg("The room is completely dark.")

    def at_object_receive(self, obj, source_location):
        """
        Called when an object enters the room.
        """
        if obj.has_account:
            # a puppeted object, that is, a Character
            self._heal(obj)
            # in case the new guy carries light with them
            self.check_light_state()

    def at_object_leave(self, obj, target_location):
        """
        In case people leave with the light, we make sure to clear the
        DarkCmdSet if necessary.  This also works if they are
        teleported away.
        """
        # since this hook is called while the object is still in the room,
        # we exclude it from the light check, to ignore any light sources
        # it may be carrying.
        self.check_light_state(exclude=obj)
