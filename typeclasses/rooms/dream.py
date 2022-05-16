

from evennia import CmdSet, Command

from typeclasses.base import Room


class CmdWake(Command):
    """
    Wake from a dream

    Usage:
      wake

    Wake from a dream.
    """

    key = "wake"
    aliases = ["w"]
    locks = "cmd:all()"
    help_category = "world"

    def func(self):
        """
        Implement the command.

        Wake 
        """
        self.caller.move_to(Room.objects.all()[1])
        self.caller.msg("You wake up feeling refreshed.")

class DreamCmdSet(CmdSet):
    """
    Groups the commands of the dream room together.
    """

    key = "dreamroom_cmdset"

    def at_cmdset_creation(self):
        """populate the cmdset."""
        self.add(CmdWake())

class DreamRoom(Room):
    """
    A dream room. You can wake up from it.
    """
    
    def at_object_creation(self):
        """
        Called when object is first created.
        """
        super().at_object_creation()
        # the room starts dark.
        self.cmdset.add(DreamCmdSet, permanent=True)
