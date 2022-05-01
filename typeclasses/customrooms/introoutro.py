from evennia import CmdSet, Command

from typeclasses.rooms import Room
from typeclasses.menus.intro_menu import init_menu


# ------------------------------------------------------------
#
# Intro Room - unique room
#
# This room marks the start of Druidia. It sets up properties on
# the player char that is needed for the game.
#
# -------------------------------------------------------------


SUPERUSER_WARNING = (
    "\nWARNING: You are playing as a superuser ({name}). Use the {quell} command to\n"
    "play without superuser privileges (many functions and puzzles ignore the \n"
    "presence of a superuser, making this mode useful for exploring things behind \n"
    "the scenes later).\n")
    
    
class CmdEvenniaIntro(Command):
    """
    Start the Evennia intro wizard.

    Usage:
        intro

    """

    key = "intro"

    def func(self):
        # quell also superusers
        if self.caller.account:
            self.caller.account.execute_cmd("quell")
            self.caller.msg("(Auto-quelling)")
        init_menu(self.caller)


class CmdSetEvenniaIntro(CmdSet):
    key = "Evennia Intro StartSet"

    def at_cmdset_creation(self):
        self.add(CmdEvenniaIntro())


class IntroRoom(Room):
    """
    Intro room

    properties to customize:
     char_health - integer > 0 (default 20)
    """

    def at_object_creation(self):
        """
        Called when the room is first created.
        """
        super().at_object_creation()
        self.cmdset.add(CmdSetEvenniaIntro, permanent=True)

    def at_object_receive(self, character, source_location):
        """
        Assign properties on characters
        """

        # setup character health.
        health = self.db.char_health or 20

        if character.has_account:
            character.db.health = health
            character.db.health_max = health

        if character.is_superuser:
            string = "-" * 78 + SUPERUSER_WARNING + "-" * 78
            character.msg("|r%s|n" %
                          string.format(name=character.key, quell="|wquell|r"))
        else:
            # quell user
            if character.account:
                character.account.execute_cmd("quell")
                character.msg("(Auto-quelling while in Druidia.)")


# -------------------------------------------------------------
#
# Outro room - unique exit room
#
# Cleans up the character from all properties et by Druidia.
#
# -------------------------------------------------------------


class OutroRoom(Room):
    """
    Outro room.

    Called when exiting Druidia, cleans the character of attributes set
    by the world during play.

    """

    def at_object_creation(self):
        """
        Called when the room is first created.
        """
        super().at_object_creation()

    def at_object_receive(self, character, source_location):
        """
        Do cleanup.
        """
        if character.has_account:
            del character.db.health_max
            del character.db.health
            del character.db.last_climbed
            del character.db.puzzle_clue
            del character.db.combat_parry_mode
            del character.db.tutorial_bridge_position
            for obj in character.contents:
                if obj.typeclass_path.startswith("."):
                    obj.delete()
            character.tags.clear(category="world")

    def at_object_leave(self, character, destination):
        if character.account:
            character.account.execute_cmd("unquell")
