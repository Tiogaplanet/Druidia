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


from evennia import CmdSet

from commands.command import Command
from typeclasses.object import Object


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
