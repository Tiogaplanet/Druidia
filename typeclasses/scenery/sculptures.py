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


from evennia import CmdSet

from commands.command import Command
from typeclasses.base import Object


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
