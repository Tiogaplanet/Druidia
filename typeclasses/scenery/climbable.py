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


from evennia import CmdSet

from commands.command import Command
from typeclasses.objects import Object


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
