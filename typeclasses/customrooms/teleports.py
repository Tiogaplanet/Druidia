# -------------------------------------------------------------
#
# Teleport room - puzzles solution
#
# This is a sort of puzzle room that requires a certain
# attribute on the entering character to be the same as
# an attribute of the room. If not, the character will
# be teleported away to a target location. This is used
# by the Obelisk - grave chamber puzzle, where one must
# have looked at the obelisk to get an attribute set on
# oneself, and then pick the grave chamber with the
# matching imagery for this attribute.
#
# -------------------------------------------------------------


from evennia import CmdSet, Command, search_object, syscmdkeys, default_cmds

from typeclasses.rooms import Room


class TeleportRoom(Room):
    """
    Teleporter - puzzle room.

    Important attributes (set at creation):
      puzzle_key    - which attr to look for on character
      puzzle_value  - what char.db.puzzle_key must be set to
      success_teleport_to -  where to teleport in case if success
      success_teleport_msg - message to echo while teleporting to success
      failure_teleport_to - where to teleport to in case of failure
      failure_teleport_msg - message to echo while teleporting to failure

    """

    def at_object_creation(self):
        """Called at first creation"""
        super().at_object_creation()
        # what character.db.puzzle_clue must be set to, to avoid teleportation.
        self.db.puzzle_value = 1
        # target of successful teleportation. Can be a dbref or a
        # unique room name.
        self.db.success_teleport_msg = "You are successful!"
        self.db.success_teleport_to = "treasure room"
        # the target of the failure teleportation.
        self.db.failure_teleport_msg = "You fail!"
        self.db.failure_teleport_to = "dark cell"

    def at_object_receive(self, character, source_location):
        """
        This hook is called by the engine whenever the player is moved into
        this room.
        """
        if not character.has_account:
            # only act on player characters.
            return
        # determine if the puzzle is a success or not
        is_success = str(character.db.puzzle_clue) == str(self.db.puzzle_value)
        teleport_to = self.db.success_teleport_to if is_success else self.db.failure_teleport_to
        # note that this returns a list
        results = search_object(teleport_to)
        if not results or len(results) > 1:
            # we cannot move anywhere since no valid target was found.
            character.msg("no valid teleport target for %s was found." %
                          teleport_to)
            return
        if character.is_superuser:
            # superusers don't get teleported
            character.msg(
                "Superuser block: You would have been teleported to %s." %
                results[0])
            return
        # perform the teleport
        if is_success:
            character.msg(self.db.success_teleport_msg)
        else:
            character.msg(self.db.failure_teleport_msg)
        # teleport quietly to the new place
        character.move_to(results[0], quiet=True, move_hooks=False)
        # we have to call this manually since we turn off move_hooks
        # - this is necessary to make the target dark room aware of an
        # already carried light.
        results[0].at_object_receive(character, self)
