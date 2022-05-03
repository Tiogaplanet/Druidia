# -------------------------------------------------------------
#
# Weather room - room with a ticker
#
# -------------------------------------------------------------


import random
from evennia import TICKER_HANDLER
from evennia import CmdSet
from evennia import utils, create_object, search_object
from evennia import syscmdkeys, default_cmds

from typeclasses.base import Room


# These are rainy weather strings
WEATHER_STRINGS = (
    "The rain coming down from the iron-grey sky intensifies.",
    "A gust of wind throws the rain right in your face. Despite your cloak you shiver.",
    "The rainfall eases a bit and the sky momentarily brightens.",
    "For a moment it looks like the rain is slowing, then it begins anew with renewed force.",
    "The rain pummels you with large, heavy drops. You hear the rumble of thunder in the distance.",
    "The wind is picking up, howling around you, throwing water droplets in your face. It's cold.",
    "Bright fingers of lightning flash over the sky, moments later followed by a deafening rumble.",
    "It rains so hard you can hardly see your hand in front of you. You'll soon be drenched to the bone.",
    "Lightning strikes in several thundering bolts, striking the trees in the forest to your west.",
    "You hear the distant howl of what sounds like some sort of dog or wolf.",
    "Large clouds rush across the sky, throwing their load of rain over the world.",
)


class WeatherRoom(Room):
    """
    This should probably better be called a rainy room...

    This sets up an outdoor room typeclass. At irregular intervals,
    the effects of weather will show in the room. Outdoor rooms should
    inherit from this.

    """

    def at_object_creation(self):
        """
        Called when object is first created.
        We set up a ticker to update this room regularly.

        Note that we could in principle also use a Script to manage
        the ticking of the room; the TickerHandler works fine for
        simple things like this though.
        """
        super().at_object_creation()
        # subscribe ourselves to a ticker to repeatedly call the hook
        # "update_weather" on this object. The interval is randomized
        # so as to not have all weather rooms update at the same time.
        self.db.interval = random.randint(50, 70)
        TICKER_HANDLER.add(
            interval=self.db.interval, callback=self.update_weather, idstring="druidia"
        )

    def update_weather(self, *args, **kwargs):
        """
        Called by the tickerhandler at regular intervals. Even so, we
        only update 20% of the time, picking a random weather message
        when we do. The tickerhandler requires that this hook accepts
        any arguments and keyword arguments (hence the *args, **kwargs
        even though we don't actually use them in this example)
        """
        if random.random() < 0.2:
            # only update 20 % of the time
            self.msg_contents("|w%s|n" % random.choice(WEATHER_STRINGS))


# -------------------------------------------------------------
#
# Bridge - unique room
#
# Defines a special west-eastward "bridge"-room, a large room that takes
# several steps to cross. It is complete with custom commands and a
# chance of falling off the bridge. This room has no regular exits,
# instead the exitings are handled by custom commands set on the account
# upon first entering the room.
#
# Since one can enter the bridge room from both ends, it is
# divided into five steps:
#       westroom <- 0 1 2 3 4 -> eastroom
#
# -------------------------------------------------------------


class CmdEast(Command):
    """
    Go eastwards across the bridge.

    Info:
        This command relies on the caller having two Attributes
        (assigned by the room when entering):
            - east_exit: a unique name or dbref to the room to go to
              when exiting east.
            - west_exit: a unique name or dbref to the room to go to
              when exiting west.
       The room must also have the following Attributes
           - tutorial_bridge_posistion: the current position on
             on the bridge, 0 - 4.

    """

    key = "east"
    aliases = ["e"]
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """move one step eastwards"""
        caller = self.caller

        bridge_step = min(5, caller.db.tutorial_bridge_position + 1)

        if bridge_step > 4:
            # we have reached the far east end of the bridge.
            # Move to the east room.
            eexit = search_object(self.obj.db.east_exit)
            if eexit:
                caller.move_to(eexit[0])
            else:
                caller.msg("No east exit was found for this room. Contact an admin.")
            return
        caller.db.tutorial_bridge_position = bridge_step
        # since we are really in one room, we have to notify others
        # in the room when we move.
        caller.location.msg_contents(
            "%s steps eastwards across the bridge." % caller.name, exclude=caller
        )
        caller.execute_cmd("look")


# go back across the bridge
class CmdWest(Command):
    """
    Go westwards across the bridge.

    Info:
       This command relies on the caller having two Attributes
       (assigned by the room when entering):
           - east_exit: a unique name or dbref to the room to go to
             when exiting east.
           - west_exit: a unique name or dbref to the room to go to
             when exiting west.
       The room must also have the following property:
           - tutorial_bridge_posistion: the current position on
             on the bridge, 0 - 4.

    """

    key = "west"
    aliases = ["w"]
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """move one step westwards"""
        caller = self.caller

        bridge_step = max(-1, caller.db.tutorial_bridge_position - 1)

        if bridge_step < 0:
            # we have reached the far west end of the bridge.
            # Move to the west room.
            wexit = search_object(self.obj.db.west_exit)
            if wexit:
                caller.move_to(wexit[0])
            else:
                caller.msg("No west exit was found for this room. Contact an admin.")
            return
        caller.db.tutorial_bridge_position = bridge_step
        # since we are really in one room, we have to notify others
        # in the room when we move.
        caller.location.msg_contents(
            "%s steps westwards across the bridge." % caller.name, exclude=caller
        )
        caller.execute_cmd("look")


BRIDGE_POS_MESSAGES = (
    "You are standing |wvery close to the the bridge's western foundation|n."
    " If you go west you will be back on solid ground ...",
    "The bridge slopes precariously where it extends eastwards"
    " towards the lowest point - the center point of the hang bridge.",
    "You are |whalfways|n out on the unstable bridge.",
    "The bridge slopes precariously where it extends westwards"
    " towards the lowest point - the center point of the hang bridge.",
    "You are standing |wvery close to the bridge's eastern foundation|n."
    " If you go east you will be back on solid ground ...",
)
BRIDGE_MOODS = (
    "The bridge sways in the wind.",
    "The hanging bridge creaks dangerously.",
    "You clasp the ropes firmly as the bridge sways and creaks under you.",
    "From the castle you hear a distant howling sound, like that of a large dog or other beast.",
    "The bridge creaks under your feet. Those planks does not seem very sturdy.",
    "Far below you the ocean roars and throws its waves against the cliff,"
    " as if trying its best to reach you.",
    "Parts of the bridge come loose behind you, falling into the chasm far below!",
    "A gust of wind causes the bridge to sway precariously.",
    "Under your feet a plank comes loose, tumbling down. For a moment you dangle over the abyss ...",
    "The section of rope you hold onto crumble in your hands,"
    " parts of it breaking apart. You sway trying to regain balance.",
)

FALL_MESSAGE = (
    "Suddenly the plank you stand on gives way under your feet! You fall!"
    "\nYou try to grab hold of an adjoining plank, but all you manage to do is to "
    "divert your fall westwards, towards the cliff face. This is going to hurt ... "
    "\n ... The world goes dark ...\n\n"
)


class CmdLookBridge(Command):
    """
    looks around at the bridge.

    Info:
        This command assumes that the room has an Attribute
        "fall_exit", a unique name or dbref to the place they end upp
        if they fall off the bridge.
    """

    key = "look"
    aliases = ["l"]
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """Looking around, including a chance to fall."""
        caller = self.caller
        bridge_position = self.caller.db.tutorial_bridge_position
        # this command is defined on the room, so we get it through self.obj
        location = self.obj
        # randomize the look-echo
        message = "|c%s|n\n%s\n%s" % (
            location.key,
            BRIDGE_POS_MESSAGES[bridge_position],
            random.choice(BRIDGE_MOODS),
        )

        chars = [
            obj for obj in self.obj.contents_get(exclude=caller) if obj.has_account
        ]
        if chars:
            # we create the You see: message manually here
            message += "\n You see: %s" % ", ".join(
                "|c%s|n" % char.key for char in chars
            )
        self.caller.msg(message)

        # there is a chance that we fall if we are on the western or central
        # part of the bridge.
        if (
            bridge_position < 3
            and random.random() < 0.05
            and not self.caller.is_superuser
        ):
            # we fall 5% of time.
            fall_exit = search_object(self.obj.db.fall_exit)
            if fall_exit:
                self.caller.msg("|r%s|n" % FALL_MESSAGE)
                self.caller.move_to(fall_exit[0], quiet=True)
                # inform others on the bridge
                self.obj.msg_contents(
                    "A plank gives way under %s's feet and "
                    "they fall from the bridge!" % self.caller.key
                )


# custom help command
class CmdBridgeHelp(Command):
    """
    Overwritten help command while on the bridge.
    """

    key = "help"
    aliases = ["h", "?"]
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """Implements the command."""
        string = (
            "You are trying hard not to fall off the bridge ..."
            "\n\nWhat you can do is trying to cross the bridge |weast|n"
            " or try to get back to the mainland |wwest|n)."
        )
        self.caller.msg(string)


class BridgeCmdSet(CmdSet):
    """This groups the bridge commands. We will store it on the room."""

    key = "Bridge commands"
    priority = 2  # this gives it precedence over the normal look/help commands.

    def at_cmdset_creation(self):
        """Called at first cmdset creation"""
        self.add(CmdEast())
        self.add(CmdWest())
        self.add(CmdLookBridge())
        self.add(CmdBridgeHelp())


BRIDGE_WEATHER = (
    "The rain intensifies, making the planks of the bridge even more slippery.",
    "A gust of wind throws the rain right in your face.",
    "The rainfall eases a bit and the sky momentarily brightens.",
    "The bridge shakes under the thunder of a closeby thunder strike.",
    "The rain pummels you with large, heavy drops. You hear the distinct howl of a large hound in the distance.",
    "The wind is picking up, howling around you and causing the bridge to sway from side to side.",
    "Some sort of large bird sweeps by overhead, giving off an eery screech. Soon it has disappeared in the gloom.",
    "The bridge sways from side to side in the wind.",
    "Below you a particularly large wave crashes into the rocks.",
    "From the ruin you hear a distant, otherwordly howl. Or maybe it was just the wind.",
)


class BridgeRoom(WeatherRoom):
    """
    The bridge room implements an unsafe bridge. It also enters the player into
    a state where they get new commands so as to try to cross the bridge.

     We want this to result in the account getting a special set of
     commands related to crossing the bridge. The result is that it
     will take several steps to cross it, despite it being represented
     by only a single room.

     We divide the bridge into steps:

        self.db.west_exit     -   -  |  -   -     self.db.east_exit
                              0   1  2  3   4

     The position is handled by a variable stored on the character
     when entering and giving special move commands will
     increase/decrease the counter until the bridge is crossed.

     We also has self.db.fall_exit, which points to a gathering
     location to end up if we happen to fall off the bridge (used by
     the CmdLookBridge command).

    """

    def at_object_creation(self):
        """Setups the room"""
        # this will start the weather room's ticker and tell
        # it to call update_weather regularly.
        super().at_object_creation()
        # this identifies the exits from the room (should be the command
        # needed to leave through that exit). These are defaults, but you
        # could of course also change them after the room has been created.
        self.db.west_exit = "cliff"
        self.db.east_exit = "gate"
        self.db.fall_exit = "cliffledge"
        # add the cmdset on the room.
        self.cmdset.add(BridgeCmdSet, permanent=True)
        # since the default Character's at_look() will access the room's
        # return_description (this skips the cmdset) when
        # first entering it, we need to explicitly turn off the room
        # as a normal view target - once inside, our own look will
        # handle all return messages.
        self.locks.add("view:false()")

    def update_weather(self, *args, **kwargs):
        """
        This is called at irregular intervals and makes the passage
        over the bridge a little more interesting.
        """
        if random.random() < 80:
            # send a message most of the time
            self.msg_contents("|w%s|n" % random.choice(BRIDGE_WEATHER))

    def at_object_receive(self, character, source_location):
        """
        This hook is called by the engine whenever the player is moved
        into this room.
        """
        if character.has_account:
            # we only run this if the entered object is indeed a player object.
            # check so our east/west exits are correctly defined.
            wexit = search_object(self.db.west_exit)
            eexit = search_object(self.db.east_exit)
            fexit = search_object(self.db.fall_exit)
            if not (wexit and eexit and fexit):
                character.msg(
                    "The bridge's exits are not properly configured. "
                    "Contact an admin. Forcing west-end placement."
                )
                character.db.tutorial_bridge_position = 0
                return
            if source_location == eexit[0]:
                # we assume we enter from the same room we will exit to
                character.db.tutorial_bridge_position = 4
            else:
                # if not from the east, then from the west!
                character.db.tutorial_bridge_position = 0
            character.execute_cmd("look")

    def at_object_leave(self, character, target_location):
        """
        This is triggered when the player leaves the bridge room.
        """
        if character.has_account:
            # clean up the position attribute
            del character.db.tutorial_bridge_position
