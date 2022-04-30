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


class Room(DefaultRoom, Object):
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
