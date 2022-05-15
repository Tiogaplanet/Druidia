from evennia import CmdSet

from commands.command import Command
from typeclasses.base import Object


class CmdSleep(Command):
    """
    Usage:
      sleep

    Sleep on a bed.
    """

    key = "sleep"
    locks = "cmd:all()"
    help_category = "world"

    def func(self):
        self.caller.msg("You lay down on the bed and fall asleep.")


class CmdWake(Command):
    """
    Usage:
      wake

    Wake from sleeping on the bed.
    """

    key = "wake"
    locks = "cmd:all()"
    help_category = "world"

    def func(self):
        self.caller.msg("You wake up feeling refreshed.")


class CmdSetBed(CmdSet):
    """
    A CmdSet for beds.
    """

    def at_cmdset_creation(self):
        """
        Called when the cmdset is created.
        """
        self.add(CmdSleep())
        self.add(CmdWake())


class Bed(Object):
    """
    This simple object is a bed (or is it?).
    """

    def at_object_creation(self):
        """
        Called when object is created. We make sure to set the needed
        Attribute and add the readable cmdset.
        """
        super().at_object_creation()
        # define a command on the object.
        self.cmdset.add_default(CmdSetBed, permanent=True)
