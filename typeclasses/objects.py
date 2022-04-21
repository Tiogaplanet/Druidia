"""

Room typeclasses for Druidia.

This module holds all "dead" object definitions for
Druidia. Object commands, Object cmdsets and relevant
parts of the role-playing system are also defined here.
See the header comment for characters.py for the full
description of the role-playing system.

Objects:

Object

Readable
Climbable
Obelisk
LightSource
CrumblingWall
Weapon
WeaponRack

"""

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

        # emoting/recog data
        self.db.pose = ""
        self.db.pose_default = "is here."

    def search(
        self,
        searchdata,
        global_search=False,
        use_nicks=True,
        typeclass=None,
        location=None,
        attribute_name=None,
        quiet=False,
        exact=False,
        candidates=None,
        nofound_string=None,
        multimatch_string=None,
        use_dbref=None,
    ):
        """
        Returns an Object matching a search string/condition, taking
        sdescs into account.
        Perform a standard object search in the database, handling
        multiple results and lack thereof gracefully. By default, only
        objects in the current `location` of `self` or its inventory are searched for.
        Args:
            searchdata (str or obj): Primary search criterion. Will be matched
                against `object.key` (with `object.aliases` second) unless
                the keyword attribute_name specifies otherwise.
                **Special strings:**
                - `#<num>`: search by unique dbref. This is always
                   a global search.
                - `me,self`: self-reference to this object
                - `<num>-<string>` - can be used to differentiate
                   between multiple same-named matches
            global_search (bool): Search all objects globally. This is overruled
                by `location` keyword.
            use_nicks (bool): Use nickname-replace (nicktype "object") on `searchdata`.
            typeclass (str or Typeclass, or list of either): Limit search only
                to `Objects` with this typeclass. May be a list of typeclasses
                for a broader search.
            location (Object or list): Specify a location or multiple locations
                to search. Note that this is used to query the *contents* of a
                location and will not match for the location itself -
                if you want that, don't set this or use `candidates` to specify
                exactly which objects should be searched.
            attribute_name (str): Define which property to search. If set, no
                key+alias search will be performed. This can be used
                to search database fields (db_ will be automatically
                appended), and if that fails, it will try to return
                objects having Attributes with this name and value
                equal to searchdata. A special use is to search for
                "key" here if you want to do a key-search without
                including aliases.
            quiet (bool): don't display default error messages - this tells the
                search method that the user wants to handle all errors
                themselves. It also changes the return value type, see
                below.
            exact (bool): if unset (default) - prefers to match to beginning of
                string rather than not matching at all. If set, requires
                exact matching of entire string.
            candidates (list of objects): this is an optional custom list of objects
                to search (filter) between. It is ignored if `global_search`
                is given. If not set, this list will automatically be defined
                to include the location, the contents of location and the
                caller's contents (inventory).
            nofound_string (str):  optional custom string for not-found error message.
            multimatch_string (str): optional custom string for multimatch error header.
            use_dbref (bool or None): If None, only turn off use_dbref if we are of a lower
                permission than Builder. Otherwise, honor the True/False value.
        Returns:
            match (Object, None or list): will return an Object/None if `quiet=False`,
                otherwise it will return a list of 0, 1 or more matches.
        Notes:
            To find Accounts, use eg. `evennia.account_search`. If
            `quiet=False`, error messages will be handled by
            `settings.SEARCH_AT_RESULT` and echoed automatically (on
            error, return will be `None`). If `quiet=True`, the error
            messaging is assumed to be handled by the caller.
        """
        is_string = isinstance(searchdata, str)

        if is_string:
            # searchdata is a string; wrap some common self-references
            if searchdata.lower() in ("here",):
                return [self.location] if quiet else self.location
            if searchdata.lower() in ("me", "self"):
                return [self] if quiet else self

        if use_nicks:
            # do nick-replacement on search
            searchdata = self.nicks.nickreplace(
                searchdata, categories=("object", "account"), include_account=True
            )

        if global_search or (
            is_string
            and searchdata.startswith("#")
            and len(searchdata) > 1
            and searchdata[1:].isdigit()
        ):
            # only allow exact matching if searching the entire database
            # or unique #dbrefs
            exact = True
        elif candidates is None:
            # no custom candidates given - get them automatically
            if location:
                # location(s) were given
                candidates = []
                for obj in make_iter(location):
                    candidates.extend(obj.contents)
            else:
                # local search. Candidates are taken from
                # self.contents, self.location and
                # self.location.contents
                location = self.location
                candidates = self.contents
                if location:
                    candidates = candidates + [location] + location.contents
                else:
                    # normally we don't need this since we are
                    # included in location.contents
                    candidates.append(self)

        # the sdesc-related substitution
        is_builder = self.locks.check_lockstring(self, "perm(Builder)")
        use_dbref = is_builder if use_dbref is None else use_dbref

        def search_obj(string):
            "helper wrapper for searching"
            return ObjectDB.objects.object_search(
                string,
                attribute_name=attribute_name,
                typeclass=typeclass,
                candidates=candidates,
                exact=exact,
                use_dbref=use_dbref,
            )

        if candidates:
            candidates = parse_sdescs_and_recogs(
                self, candidates, _PREFIX + searchdata, search_mode=True
            )
            results = []
            for candidate in candidates:
                # we search by candidate keys here; this allows full error
                # management and use of all kwargs - we will use searchdata
                # in eventual error reporting later (not their keys). Doing
                # it like this e.g. allows for use of the typeclass kwarg
                # limiter.
                results.extend(
                    [obj for obj in search_obj(candidate.key) if obj not in results]
                )

            if not results and is_builder:
                # builders get a chance to search only by key+alias
                results = search_obj(searchdata)
        else:
            # global searches / #drefs end up here. Global searches are
            # only done in code, so is controlled, #dbrefs are turned off
            # for non-Builders.
            results = search_obj(searchdata)

        if quiet:
            return results
        return _AT_SEARCH_RESULT(
            results,
            self,
            query=searchdata,
            nofound_string=nofound_string,
            multimatch_string=multimatch_string,
        )

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.
        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.
        Keyword Args:
            pose (bool): Include the pose (if available) in the return.
        Returns:
            name (str): A string of the sdesc containing the name of the object,
            if this is defined.
                including the DBREF if this user is privileged to control
                said object.
        Notes:
            The RPObject version doesn't add color to its display.
        """
        idstr = "(#%s)" % self.id if self.access(looker, access_type="control") else ""
        if looker == self:
            sdesc = self.key
        else:
            try:
                recog = looker.recog.get(self)
            except AttributeError:
                recog = None
            sdesc = recog or (hasattr(self, "sdesc") and self.sdesc.get()) or self.key
        pose = " %s" % (self.db.pose or "") if kwargs.get("pose", False) else ""
        return "%s%s%s" % (sdesc, idstr, pose)

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (
            con for con in self.contents if con != looker and con.access(looker, "view")
        )
        exits, users, things = [], [], []
        for con in visible:
            key = con.get_display_name(looker, pose=True)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append(key)
            else:
                things.append(key)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker, pose=True)
        desc = self.db.desc
        if desc:
            string += "%s" % desc
        if exits:
            string += "\n|wExits:|n " + ", ".join(exits)
        if users or things:
            string += "\n " + "\n ".join(users + things)
        return string

    def reset(self):
        """Resets the object, whatever that may mean."""
        self.location = self.home


# -------------------------------------------------------------
#
# Readable - an object that can be "read"
#
# -------------------------------------------------------------

#
# Read command
#


class CmdRead(Command):
    """
    Usage:
      read [obj]

    Read some text of a readable object.
    """

    key = "read"
    locks = "cmd:all()"
    help_category = "world"

    def func(self):
        """
        Implements the read command. This simply looks for an
        Attribute "readable_text" on the object and displays that.
        """

        if self.args:
            obj = self.caller.search(self.args.strip())
        else:
            obj = self.obj
        if not obj:
            return
        # we want an attribute read_text to be defined.
        readtext = obj.db.readable_text
        if readtext:
            string = "You read |C%s|n:\n  %s" % (obj.key, readtext)
        else:
            string = "There is nothing to read on %s." % obj.key
        self.caller.msg(string)


class CmdSetReadable(CmdSet):
    """
    A CmdSet for readables.
    """

    def at_cmdset_creation(self):
        """
        Called when the cmdset is created.
        """
        self.add(CmdRead())


class Readable(Object):
    """
    This simple object defines some attributes and
    """

    def at_object_creation(self):
        """
        Called when object is created. We make sure to set the needed
        Attribute and add the readable cmdset.
        """
        super().at_object_creation()
        self.db.readable_text = "There is no text written on %s." % self.key
        # define a command on the object.
        self.cmdset.add_default(CmdSetReadable, permanent=True)


# -------------------------------------------------------------
#
# Climbable object
#
# The climbable object works so that once climbed, it sets
# a flag on the climber to show that it was climbed. A simple
# command 'climb' handles the actual climbing. The memory
# of what was last climbed is used in a simple puzzle in
# Druidia.
#
# -------------------------------------------------------------


class CmdClimb(Command):
    """
    Climb an object

    Usage:
      climb <object>

    This allows you to climb.
    """

    key = "climb"
    locks = "cmd:all()"
    help_category = "world"

    def func(self):
        """Implements function"""

        if not self.args:
            self.caller.msg("What do you want to climb?")
            return
        obj = self.caller.search(self.args.strip())
        if not obj:
            return
        if obj != self.obj:
            self.caller.msg("Try as you might, you cannot climb that.")
            return
        ostring = self.obj.db.climb_text
        if not ostring:
            ostring = (
                "You climb %s. Having looked around, you climb down again."
                % self.obj.name
            )
        self.caller.msg(ostring)
        # set a tag on the caller to remember that we climbed.
        self.caller.tags.add("tutorial_climbed_tree", category="world")


class CmdSetClimbable(CmdSet):
    """Climbing cmdset"""

    def at_cmdset_creation(self):
        """populate set"""
        self.add(CmdClimb())


class Climbable(Object):
    """
    A climbable object. All that is special about it is that it has
    the "climb" command available on it.
    """

    def at_object_creation(self):
        """Called at initial creation only"""
        self.cmdset.add_default(CmdSetClimbable, permanent=True)


# -------------------------------------------------------------
#
# Obelisk - a unique item
#
# The Obelisk is an object with a modified return_appearance method
# that causes it to look slightly different every time one looks at it.
# Since what you actually see is a part of a game puzzle, the act of
# looking also stores a key attribute on the looking object (different
# depending on which text you saw) for later reference.
#
# -------------------------------------------------------------


class Obelisk(Object):
    """
    This object changes its description randomly, and which is shown
    determines which order "clue id" is stored on the Character for
    future puzzles.

    Important Attribute:
       puzzle_descs (list): list of descriptions. One of these is
        picked randomly when this object is looked at and its index
        in the list is used as a key for to solve the puzzle.

    """

    def at_object_creation(self):
        """Called when object is created."""
        super().at_object_creation()
        self.db.puzzle_descs = ["You see a normal stone slab"]
        # make sure this can never be picked up
        self.locks.add("get:false()")

    def return_appearance(self, caller):
        """
        This hook is called by the look command to get the description
        of the object. We overload it with our own version.
        """
        # randomly get the index for one of the descriptions
        descs = self.db.puzzle_descs
        clueindex = random.randint(0, len(descs) - 1)
        # set this description, with the random extra
        string = (
            "The surface of the obelisk seem to waver, shift and writhe under your gaze, with "
            "different scenes and structures appearing whenever you look at it. "
        )
        self.db.desc = string + descs[clueindex]
        # remember that this was the clue we got. The Puzzle room will
        # look for this later to determine if you should be teleported
        # or not.
        caller.db.puzzle_clue = clueindex
        # call the parent function as normal (this will use
        # the new desc Attribute we just set)
        return super().return_appearance(caller)


# -------------------------------------------------------------
#
# LightSource
#
# This object emits light. Once it has been turned on it
# cannot be turned off. When it burns out it will delete
# itself.
#
# This could be implemented using a single-repeat Script or by
# registering with the TickerHandler. We do it simpler by
# using the delay() utility function. This is very simple
# to use but does not survive a server @reload. Because of
# where the light matters (in the Dark Room where you can
# find new light sources easily), this is okay here.
#
# -------------------------------------------------------------


class CmdLight(Command):
    """
    Creates light where there was none. Something to burn.
    """

    key = "on"
    aliases = ["light", "burn"]
    # only allow this command if command.obj is carried by caller.
    locks = "cmd:holds()"
    help_category = "World"

    def func(self):
        """
        Implements the light command. Since this command is designed
        to sit on a "lightable" object, we operate only on self.obj.
        """

        if self.obj.light():
            self.caller.msg("You light %s." % self.obj.key)
            self.caller.location.msg_contents(
                "%s lights %s!" % (self.caller, self.obj.key), exclude=[self.caller]
            )
        else:
            self.caller.msg("%s is already burning." % self.obj.key)


class CmdSetLight(CmdSet):
    """CmdSet for the lightsource commands"""

    key = "lightsource_cmdset"
    # this is higher than the dark cmdset - important!
    priority = 3

    def at_cmdset_creation(self):
        """called at cmdset creation"""
        self.add(CmdLight())


class LightSource(Object):
    """
    This implements a light source object.

    When burned out, the object will be deleted.
    """

    def at_init(self):
        """
        If this is called with the Attribute is_giving_light already
        set, we know that the timer got killed by a server
        reload/reboot before it had time to finish. So we kill it here
        instead. This is the price we pay for the simplicity of the
        non-persistent delay() method.
        """
        if self.db.is_giving_light:
            self.delete()

    def at_object_creation(self):
        """Called when object is first created."""
        super().at_object_creation()
        self.db.is_giving_light = False
        self.db.burntime = 60 * 3  # 3 minutes
        # this is the default desc, it can of course be customized
        # when created.
        self.db.desc = (
            "A splinter of wood with remnants of resin on it, enough for burning."
        )
        # add the Light command
        self.cmdset.add_default(CmdSetLight, permanent=True)

    def _burnout(self):
        """
        This is called when this light source burns out. We make no
        use of the return value.
        """
        # delete ourselves from the database
        self.db.is_giving_light = False
        try:
            self.location.location.msg_contents(
                "%s's %s flickers and dies." % (self.location, self.key),
                exclude=self.location,
            )
            self.location.msg("Your %s flickers and dies." % self.key)
            self.location.location.check_light_state()
        except AttributeError:
            try:
                self.location.msg_contents(
                    "A %s on the floor flickers and dies." % self.key
                )
                self.location.location.check_light_state()
            except AttributeError:
                # Mainly happens if we happen to be in a None location
                pass
        self.delete()

    def light(self):
        """
        Light this object - this is called by Light command.
        """
        if self.db.is_giving_light:
            return False
        # burn for 3 minutes before calling _burnout
        self.db.is_giving_light = True
        # if we are in a dark room, trigger its light check
        try:
            self.location.location.check_light_state()
        except AttributeError:
            try:
                # maybe we are directly in the room
                self.location.check_light_state()
            except AttributeError:
                # we are in a None location
                pass
        finally:
            # start the burn timer. When it runs out, self._burnout
            # will be called. We store the deferred so it can be
            # killed in unittesting.
            self.deferred = delay(60 * 3, self._burnout)
        return True


# -------------------------------------------------------------
#
# Crumbling wall - unique exit
#
# This implements a simple puzzle exit that needs to be
# accessed with commands before one can get to traverse it.
#
# The puzzle-part is simply to move roots (that have
# presumably covered the wall) aside until a button for a
# secret door is revealed. The original position of the
# roots blocks the button, so they have to be moved to a certain
# position - when they have, the "press button" command
# is made available and the Exit is made traversable.
#
# -------------------------------------------------------------

# There are four roots - two horizontal and two vertically
# running roots. Each can have three positions: top/middle/bottom
# and left/middle/right respectively. There can be any number of
# roots hanging through the middle position, but only one each
# along the sides. The goal is to make the center position clear.
# (yes, it's really as simple as it sounds, just move the roots
# to each side to "win".)
#
# The ShiftRoot command depends on the root object having an
# Attribute root_pos (a dictionary) to describe the current
# position of the roots.


class CmdShiftRoot(Command):
    """
    Shifts roots around.

    Usage:
      shift blue root left/right
      shift red root left/right
      shift yellow root up/down
      shift green root up/down

    """

    key = "shift"
    aliases = ["shiftroot", "push", "pull", "move"]
    # we only allow to use this command while the
    # room is properly lit, so we lock it to the
    # setting of Attribute "is_lit" on our location.
    locks = "cmd:locattr(is_lit)"
    help_category = "World"

    def parse(self):
        """
        Custom parser; split input by spaces for simplicity.
        """
        self.arglist = self.args.strip().split()

    def func(self):
        """
        Implement the command.
          blue/red - vertical roots
          yellow/green - horizontal roots
        """

        if not self.arglist:
            self.caller.msg("What do you want to move, and in what direction?")
            return

        if "root" in self.arglist:
            # we clean out the use of the word "root"
            self.arglist.remove("root")

        # we accept arguments on the form <color> <direction>

        if not len(self.arglist) > 1:
            self.caller.msg(
                "You must define which colour of root you want to move, and in which direction."
            )
            return

        color = self.arglist[0].lower()
        direction = self.arglist[1].lower()

        # get current root positions dict
        root_pos = self.obj.db.root_pos

        if color not in root_pos:
            self.caller.msg("No such root to move.")
            return

        # first, vertical roots (red/blue) - can be moved left/right
        if color == "red":
            if direction == "left":
                root_pos[color] = max(-1, root_pos[color] - 1)
                self.caller.msg("You shift the reddish root to the left.")
                if root_pos[color] != 0 and root_pos[color] == root_pos["blue"]:
                    root_pos["blue"] += 1
                    self.caller.msg(
                        "The root with blue flowers gets in the way and is pushed to the right."
                    )
            elif direction == "right":
                root_pos[color] = min(1, root_pos[color] + 1)
                self.caller.msg("You shove the reddish root to the right.")
                if root_pos[color] != 0 and root_pos[color] == root_pos["blue"]:
                    root_pos["blue"] -= 1
                    self.caller.msg(
                        "The root with blue flowers gets in the way and is pushed to the left."
                    )
            else:
                self.caller.msg(
                    "The root hangs straight down - you can only move it left or right."
                )
        elif color == "blue":
            if direction == "left":
                root_pos[color] = max(-1, root_pos[color] - 1)
                self.caller.msg(
                    "You shift the root with small blue flowers to the left."
                )
                if root_pos[color] != 0 and root_pos[color] == root_pos["red"]:
                    root_pos["red"] += 1
                    self.caller.msg(
                        "The reddish root is too big to fit as well, so that one falls away to the left."
                    )
            elif direction == "right":
                root_pos[color] = min(1, root_pos[color] + 1)
                self.caller.msg(
                    "You shove the root adorned with small blue flowers to the right."
                )
                if root_pos[color] != 0 and root_pos[color] == root_pos["red"]:
                    root_pos["red"] -= 1
                    self.caller.msg(
                        "The thick reddish root gets in the way and is pushed back to the left."
                    )
            else:
                self.caller.msg(
                    "The root hangs straight down - you can only move it left or right."
                )

        # now the horizontal roots (yellow/green). They can be moved up/down
        elif color == "yellow":
            if direction == "up":
                root_pos[color] = max(-1, root_pos[color] - 1)
                self.caller.msg("You shift the root with small yellow flowers upwards.")
                if root_pos[color] != 0 and root_pos[color] == root_pos["green"]:
                    root_pos["green"] += 1
                    self.caller.msg("The green weedy root falls down.")
            elif direction == "down":
                root_pos[color] = min(1, root_pos[color] + 1)
                self.caller.msg(
                    "You shove the root adorned with small yellow flowers downwards."
                )
                if root_pos[color] != 0 and root_pos[color] == root_pos["green"]:
                    root_pos["green"] -= 1
                    self.caller.msg(
                        "The weedy green root is shifted upwards to make room."
                    )
            else:
                self.caller.msg(
                    "The root hangs across the wall - you can only move it up or down."
                )
        elif color == "green":
            if direction == "up":
                root_pos[color] = max(-1, root_pos[color] - 1)
                self.caller.msg("You shift the weedy green root upwards.")
                if root_pos[color] != 0 and root_pos[color] == root_pos["yellow"]:
                    root_pos["yellow"] += 1
                    self.caller.msg("The root with yellow flowers falls down.")
            elif direction == "down":
                root_pos[color] = min(1, root_pos[color] + 1)
                self.caller.msg("You shove the weedy green root downwards.")
                if root_pos[color] != 0 and root_pos[color] == root_pos["yellow"]:
                    root_pos["yellow"] -= 1
                    self.caller.msg(
                        "The root with yellow flowers gets in the way and is pushed upwards."
                    )
            else:
                self.caller.msg(
                    "The root hangs across the wall - you can only move it up or down."
                )

        # we have moved the root. Store new position
        self.obj.db.root_pos = root_pos

        # Check victory condition
        if list(root_pos.values()).count(0) == 0:  # no roots in middle position
            # This will affect the cmd: lock of CmdPressButton
            self.obj.db.button_exposed = True
            self.caller.msg(
                "Holding aside the root you think you notice something behind it ..."
            )


class CmdPressButton(Command):
    """
    Presses a button.
    """

    key = "press"
    aliases = ["press button", "button", "push button"]
    # only accessible if the button was found and there is light. This checks
    # the Attribute button_exposed on the Wall object so that
    # you can only push the button when the puzzle is solved. It also
    # checks the is_lit Attribute on the location.
    locks = "cmd:objattr(button_exposed) and objlocattr(is_lit)"
    help_category = "World"

    def func(self):
        """Implements the command"""

        if self.caller.db.crumbling_wall_found_exit:
            # we already pushed the button
            self.caller.msg(
                "The button folded away when the secret passage opened. You cannot push it again."
            )
            return

        # pushing the button
        string = (
            "You move your fingers over the suspicious depression, then gives it a "
            "decisive push. First nothing happens, then there is a rumble and a hidden "
            "|wpassage|n opens, dust and pebbles rumbling as part of the wall moves aside."
        )
        self.caller.msg(string)
        string = (
            "%s moves their fingers over the suspicious depression, then gives it a "
            "decisive push. First nothing happens, then there is a rumble and a hidden "
            "|wpassage|n opens, dust and pebbles rumbling as part of the wall moves aside."
        )
        self.caller.location.msg_contents(string % self.caller.key, exclude=self.caller)
        if not self.obj.open_wall():
            self.caller.msg(
                "The exit leads nowhere, there's just more stone behind it ..."
            )


class CmdSetCrumblingWall(CmdSet):
    """Group the commands for crumblingWall"""

    key = "crumblingwall_cmdset"
    priority = 2

    def at_cmdset_creation(self):
        """called when object is first created."""
        self.add(CmdShiftRoot())
        self.add(CmdPressButton())


class CrumblingWall(Object, DefaultExit):
    """
    This is a custom Exit.

    The CrumblingWall can be examined in various ways, but only if a
    lit light source is in the room. The traversal itself is blocked
    by a traverse: lock on the exit that only allows passage if a
    certain attribute is set on the trying account.

    Important attribute
     destination - this property must be set to make this a valid exit
                   whenever the button is pushed (this hides it as an exit
                   until it actually is)
    """

    def at_init(self):
        """
        Called when object is recalled from cache.
        """
        self.reset()

    def at_object_creation(self):
        """called when the object is first created."""
        super().at_object_creation()

        self.aliases.add(["secret passage", "passage", "crack", "opening", "secret"])

        # starting root positions. H1/H2 are the horizontally hanging roots,
        # V1/V2 the vertically hanging ones. Each can have three positions:
        # (-1, 0, 1) where 0 means the middle position. yellow/green are
        # horizontal roots and red/blue vertical, all may have value 0, but n
        # ever any other identical value.
        self.db.root_pos = {"yellow": 0, "green": 0, "red": 0, "blue": 0}

        # flags controlling the puzzle victory conditions
        self.db.button_exposed = False
        self.db.exit_open = False

        # this is not even an Exit until it has a proper destination, and we won't assign
        # that until it is actually open. Until then we store the destination here. This
        # should be given a reasonable value at creation!
        self.db.destination = "#2"

        # we lock this Exit so that one can only execute commands on it
        # if its location is lit and only traverse it once the Attribute
        # exit_open is set to True.
        self.locks.add("cmd:locattr(is_lit);traverse:objattr(exit_open)")
        # set cmdset
        self.cmdset.add(CmdSetCrumblingWall, permanent=True)

    def open_wall(self):
        """
        This method is called by the push button command once the puzzle
        is solved. It opens the wall and sets a timer for it to reset
        itself.
        """
        # this will make it into a proper exit (this returns a list)
        eloc = search.search_object(self.db.destination)
        if not eloc:
            return False
        else:
            self.destination = eloc[0]
        self.db.exit_open = True
        # start a 45 second timer before closing again. We store the deferred so it can be
        # killed in unittesting.
        self.deferred = delay(45, self.reset)
        return True

    def _translate_position(self, root, ipos):
        """Translates the position into words"""
        rootnames = {
            "red": "The |rreddish|n vertical-hanging root ",
            "blue": "The thick vertical root with |bblue|n flowers ",
            "yellow": "The thin horizontal-hanging root with |yyellow|n flowers ",
            "green": "The weedy |ggreen|n horizontal root ",
        }
        vpos = {
            -1: "hangs far to the |wleft|n on the wall.",
            0: "hangs straight down the |wmiddle|n of the wall.",
            1: "hangs far to the |wright|n of the wall.",
        }
        hpos = {
            -1: "covers the |wupper|n part of the wall.",
            0: "passes right over the |wmiddle|n of the wall.",
            1: "nearly touches the floor, near the |wbottom|n of the wall.",
        }

        if root in ("yellow", "green"):
            string = rootnames[root] + hpos[ipos]
        else:
            string = rootnames[root] + vpos[ipos]
        return string

    def return_appearance(self, caller):
        """
        This is called when someone looks at the wall. We need to echo the
        current root positions.
        """
        if self.db.button_exposed:
            # we found the button by moving the roots
            result = [
                "Having moved all the roots aside, you find that the center of the wall, "
                "previously hidden by the vegetation, hid a curious square depression. It was maybe once "
                "concealed and made to look a part of the wall, but with the crumbling of stone around it, "
                "it's now easily identifiable as some sort of button."
            ]
        elif self.db.exit_open:
            # we pressed the button; the exit is open
            result = [
                "With the button pressed, a crack has opened in the root-covered wall, just wide enough "
                "to squeeze through. A cold draft is coming from the hole and you get the feeling the "
                "opening may close again soon."
            ]
        else:
            # puzzle not solved yet.
            result = [
                "The wall is old and covered with roots that here and there have permeated the stone. "
                "The roots (or whatever they are - some of them are covered in small nondescript flowers) "
                "crisscross the wall, making it hard to clearly see its stony surface. Maybe you could "
                "try to |wshift|n or |wmove|n them (like '|wshift red up|n').\n"
            ]
            # display the root positions to help with the puzzle
            for key, pos in self.db.root_pos.items():
                result.append("\n" + self._translate_position(key, pos))
        self.db.desc = "".join(result)

        # call the parent to continue execution (will use the desc we just set)
        return super().return_appearance(caller)

    def at_after_traverse(self, traverser, source_location):
        """
        This is called after we traversed this exit. Cleans up and resets
        the puzzle.
        """
        del traverser.db.crumbling_wall_found_buttothe
        del traverser.db.crumbling_wall_found_exit
        self.reset()

    def at_failed_traverse(self, traverser):
        """This is called if the account fails to pass the Exit."""
        traverser.msg(
            "No matter how you try, you cannot force yourself through %s." % self.key
        )

    def reset(self):
        """
        Called by world runner, or whenever someone successfully
        traversed the Exit.
        """
        self.location.msg_contents(
            "The secret door closes abruptly, roots falling back into place."
        )

        # reset the flags and remove the exit destination
        self.db.button_exposed = False
        self.db.exit_open = False
        self.destination = None

        # Reset the roots with some random starting positions for the roots:
        start_pos = [
            {"yellow": 1, "green": 0, "red": 0, "blue": 0},
            {"yellow": 0, "green": 0, "red": 0, "blue": 0},
            {"yellow": 0, "green": 1, "red": -1, "blue": 0},
            {"yellow": 1, "green": 0, "red": 0, "blue": 0},
            {"yellow": 0, "green": 0, "red": 0, "blue": 1},
        ]
        self.db.root_pos = random.choice(start_pos)


# -------------------------------------------------------------
#
# Weapon - object type
#
# A weapon (which here is assumed to be a bladed melee weapon for close
# combat) has three commands, stab, slash and defend. Weapons also have
# a property "magic" to determine if they are usable against certain
# enemies.
#
# Since Characters don't have special skills (yet), we let the weapon
# itself determine how easy/hard it is to hit with it, and how much
# damage it can do.
#
# -------------------------------------------------------------


class CmdAttack(Command):
    """
    Attack the enemy. Commands:

      stab <enemy>
      slash <enemy>
      parry

    stab - (thrust) makes a lot of damage but is harder to hit with.
    slash - is easier to land, but does not make as much damage.
    parry - forgoes your attack but will make you harder to hit on next
            enemy attack.

    """

    # this is an example of implementing many commands as a single
    # command class, using the given command alias to separate between them.

    key = "attack"
    aliases = [
        "hit",
        "kill",
        "fight",
        "thrust",
        "pierce",
        "stab",
        "slash",
        "chop",
        "bash",
        "parry",
        "defend",
    ]
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """Implements the stab"""

        cmdstring = self.cmdstring

        if cmdstring in ("attack", "fight"):
            string = (
                "How do you want to fight? Choose one of 'stab', 'slash' or 'defend'."
            )
            self.caller.msg(string)
            return

        # parry mode
        if cmdstring in ("parry", "defend"):
            string = "You raise your weapon in a defensive pose, ready to block the next enemy attack."
            self.caller.msg(string)
            self.caller.db.combat_parry_mode = True
            self.caller.location.msg_contents(
                "%s takes a defensive stance" % self.caller, exclude=[self.caller]
            )
            return

        if not self.args:
            self.caller.msg("Who do you attack?")
            return
        target = self.caller.search(self.args.strip())
        if not target:
            return

        if cmdstring in ("thrust", "pierce", "stab"):
            hit = float(self.obj.db.hit) * 0.7  # modified due to stab
            damage = self.obj.db.damage * 2  # modified due to stab
            string = "You stab with %s. " % self.obj.key
            tstring = "%s stabs at you with %s. " % (self.caller.key, self.obj.key)
            ostring = "%s stabs at %s with %s. " % (
                self.caller.key,
                target.key,
                self.obj.key,
            )
            self.caller.db.combat_parry_mode = False
        elif cmdstring in ("slash", "chop", "bash"):
            hit = float(self.obj.db.hit)  # un modified due to slash
            damage = self.obj.db.damage  # un modified due to slash
            string = "You slash with %s. " % self.obj.key
            tstring = "%s slash at you with %s. " % (self.caller.key, self.obj.key)
            ostring = "%s slash at %s with %s. " % (
                self.caller.key,
                target.key,
                self.obj.key,
            )
            self.caller.db.combat_parry_mode = False
        else:
            self.caller.msg(
                "You fumble with your weapon, unsure of whether to stab, slash or parry ..."
            )
            self.caller.location.msg_contents(
                "%s fumbles with their weapon." % self.caller, exclude=self.caller
            )
            self.caller.db.combat_parry_mode = False
            return

        if target.db.combat_parry_mode:
            # target is defensive; even harder to hit!
            target.msg("|GYou defend, trying to avoid the attack.|n")
            hit *= 0.5

        if random.random() <= hit:
            self.caller.msg(string + "|gIt's a hit!|n")
            target.msg(tstring + "|rIt's a hit!|n")
            self.caller.location.msg_contents(
                ostring + "It's a hit!", exclude=[target, self.caller]
            )

            # call enemy hook
            if hasattr(target, "at_hit"):
                # should return True if target is defeated, False otherwise.
                target.at_hit(self.obj, self.caller, damage)
                return
            elif target.db.health:
                target.db.health -= damage
            else:
                # sorry, impossible to fight this enemy ...
                self.caller.msg("The enemy seems unaffected.")
                return
        else:
            self.caller.msg(string + "|rYou miss.|n")
            target.msg(tstring + "|gThey miss you.|n")
            self.caller.location.msg_contents(
                ostring + "They miss.", exclude=[target, self.caller]
            )


class CmdSetWeapon(CmdSet):
    """Holds the attack command."""

    def at_cmdset_creation(self):
        """called at first object creation."""
        self.add(CmdAttack())


class Weapon(Object):
    """
    This defines a bladed weapon.

    Important attributes (set at creation):
      hit - chance to hit (0-1)
      parry - chance to parry (0-1)
      damage - base damage given (modified by hit success and
               type of attack) (0-10)

    """

    def at_object_creation(self):
        """Called at first creation of the object"""
        super().at_object_creation()
        self.db.hit = 0.4  # hit chance
        self.db.parry = 0.8  # parry chance
        self.db.damage = 1.0
        self.db.magic = False
        self.cmdset.add_default(CmdSetWeapon, permanent=True)

    def reset(self):
        """
        When reset, the weapon is simply deleted, unless it has a place
        to return to.
        """
        if self.location.has_account and self.home == self.location:
            self.location.msg_contents(
                "%s suddenly and magically fades into nothingness, as if it was never there ..."
                % self.key
            )
            self.delete()
        else:
            self.location = self.home


# -------------------------------------------------------------
#
# Weapon rack - spawns weapons
#
# This is a spawner mechanism that creates custom weapons from a
# spawner prototype dictionary. Note that we only create a single typeclass
# (Weapon) yet customize all these different weapons using the spawner.
# The spawner dictionaries could easily sit in separate modules and be
# used to create unique and interesting variations of typeclassed
# objects.
#
# -------------------------------------------------------------

WEAPON_PROTOTYPES = {
    "weapon": {
        "typeclass": "objects.Weapon",
        "key": "Weapon",
        "hit": 0.2,
        "parry": 0.2,
        "damage": 1.0,
        "magic": False,
        "desc": "A generic blade.",
    },
    "knife": {
        "prototype_parent": "weapon",
        "aliases": "sword",
        "key": "Kitchen knife",
        "desc": "A rusty kitchen knife. Better than nothing.",
        "damage": 3,
    },
    "dagger": {
        "prototype_parent": "knife",
        "key": "Rusty dagger",
        "aliases": ["knife", "dagger"],
        "desc": "A double-edged dagger with a nicked edge and a wooden handle.",
        "hit": 0.25,
    },
    "sword": {
        "prototype_parent": "weapon",
        "key": "Rusty sword",
        "aliases": ["sword"],
        "desc": "A rusty shortsword. It has a leather-wrapped handle covered i food grease.",
        "hit": 0.3,
        "damage": 5,
        "parry": 0.5,
    },
    "club": {
        "prototype_parent": "weapon",
        "key": "Club",
        "desc": "A heavy wooden club, little more than a heavy branch.",
        "hit": 0.4,
        "damage": 6,
        "parry": 0.2,
    },
    "axe": {
        "prototype_parent": "weapon",
        "key": "Axe",
        "desc": "A woodcutter's axe with a keen edge.",
        "hit": 0.4,
        "damage": 6,
        "parry": 0.2,
    },
    "ornate longsword": {
        "prototype_parent": "sword",
        "key": "Ornate longsword",
        "desc": "A fine longsword with some swirling patterns on the handle.",
        "hit": 0.5,
        "magic": True,
        "damage": 5,
    },
    "warhammer": {
        "prototype_parent": "club",
        "key": "Silver Warhammer",
        "aliases": ["hammer", "warhammer", "war"],
        "desc": "A heavy war hammer with silver ornaments. This huge weapon causes massive damage - if you can hit.",
        "hit": 0.4,
        "magic": True,
        "damage": 8,
    },
    "rune axe": {
        "prototype_parent": "axe",
        "key": "Runeaxe",
        "aliases": ["axe"],
        "hit": 0.4,
        "magic": True,
        "damage": 6,
    },
    "thruning": {
        "prototype_parent": "ornate longsword",
        "key": "Broadsword named Thruning",
        "desc": "This heavy bladed weapon is marked with the name 'Thruning'. It is very powerful in skilled hands.",
        "hit": 0.6,
        "parry": 0.6,
        "damage": 7,
    },
    "slayer waraxe": {
        "prototype_parent": "rune axe",
        "key": "Slayer waraxe",
        "aliases": ["waraxe", "war", "slayer"],
        "desc": "A huge double-bladed axe marked with the runes for 'Slayer'."
        " It has more runic inscriptions on its head, which you cannot decipher.",
        "hit": 0.7,
        "damage": 8,
    },
    "ghostblade": {
        "prototype_parent": "ornate longsword",
        "key": "The Ghostblade",
        "aliases": ["blade", "ghost"],
        "desc": "This massive sword is large as you are tall, yet seems to weigh almost nothing."
        " It's almost like it's not really there.",
        "hit": 0.9,
        "parry": 0.8,
        "damage": 10,
    },
    "hawkblade": {
        "prototype_parent": "ghostblade",
        "key": "The Hawkblade",
        "aliases": ["hawk", "blade"],
        "desc": "The weapon of a long-dead heroine and a more civilized age,"
        " the hawk-shaped hilt of this blade almost has a life of its own.",
        "hit": 0.85,
        "parry": 0.7,
        "damage": 11,
    },
}


class CmdGetWeapon(Command):
    """
    Usage:
      get weapon

    This will try to obtain a weapon from the container.
    """

    key = "get weapon"
    aliases = "get weapon"
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """
        Get a weapon from the container. It will
        itself handle all messages.
        """
        self.obj.produce_weapon(self.caller)


class CmdSetWeaponRack(CmdSet):
    """
    The cmdset for the rack.
    """

    key = "weaponrack_cmdset"

    def at_cmdset_creation(self):
        """Called at first creation of cmdset"""
        self.add(CmdGetWeapon())


class WeaponRack(Object):
    """
    This object represents a weapon store. When people use the
    "get weapon" command on this rack, it will produce one
    random weapon from among those registered to exist
    on it. This will also set a property on the character
    to make sure they can't get more than one at a time.

    Attributes to set on this object:
        available_weapons: list of prototype-keys from
            WEAPON_PROTOTYPES, the weapons available in this rack.
        no_more_weapons_msg - error message to return to accounts
            who already got one weapon from the rack and tries to
            grab another one.

    """

    def at_object_creation(self):
        """
        called at creation
        """
        self.cmdset.add_default(CmdSetWeaponRack, permanent=True)
        self.db.rack_id = "weaponrack_1"
        # these are prototype names from the prototype
        # dictionary above.
        self.db.get_weapon_msg = dedent(
            """
            You find |c%s|n. While carrying this weapon, these actions are available:
              |wstab/thrust/pierce <target>|n - poke at the enemy. More damage but harder to hit.
              |wslash/chop/bash <target>|n - swipe at the enemy. Less damage but easier to hit.
              |wdefend/parry|n - protect yourself and make yourself harder to hit.)
            """
        ).strip()

        self.db.no_more_weapons_msg = "you find nothing else of use."
        self.db.available_weapons = ["knife", "dagger", "sword", "club"]

    def produce_weapon(self, caller):
        """
        This will produce a new weapon from the rack,
        assuming the caller hasn't already gotten one. When
        doing so, the caller will get Tagged with the id
        of this rack, to make sure they cannot keep
        pulling weapons from it indefinitely.
        """
        rack_id = self.db.rack_id
        if caller.tags.get(rack_id, category="world"):
            caller.msg(self.db.no_more_weapons_msg)
        else:
            prototype = random.choice(self.db.available_weapons)
            # use the spawner to create a new Weapon from the
            # spawner dictionary, tag the caller
            wpn = spawn(
                WEAPON_PROTOTYPES[prototype], prototype_parents=WEAPON_PROTOTYPES
            )[0]
            caller.tags.add(rack_id, category="world")
            wpn.location = caller
            caller.msg(self.db.get_weapon_msg % wpn.key)
