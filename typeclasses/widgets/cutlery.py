from evennia import CmdSet

from commands.command import Command
from typeclasses.base import Object


class CmdBend(Command):
    """
    Usage:
      bend [obj]

    Read some text of a readable object.
    """

    key = "bend"
    locks = "cmd:all()"
    help_category = "world"

    def func(self):
        self.caller.msg("There is no spoon.")


class CmdSetSpoon(CmdSet):
    """
    A CmdSet for spoons.
    """

    def at_cmdset_creation(self):
        """
        Called when the cmdset is created.
        """
        self.add(CmdBend())


class Spoon(Object):
    """
    This simple object is a spoon (or is it?).
    """

    def at_object_creation(self):
        """
        Called when object is created. We make sure to set the needed
        Attribute and add the readable cmdset.
        """
        super().at_object_creation()
        # define a command on the object.
        self.cmdset.add_default(CmdSetSpoon, permanent=True)
