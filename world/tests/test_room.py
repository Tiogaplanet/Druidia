# test tutorial_world/
from evennia import create_object
from evennia.commands.default.tests import CommandTest

from typeclasses import base as drubase


class TestRoom(CommandTest):
    def test_room(self):
        room = create_object(drubase.Room, key="room")
        self.char1.location = room
        self.call(
            drubase.CmdSetDetail(),
            "detail;foo;foo2 = A detail",
            "Detail set: 'detail;foo;foo2': 'A detail'",
            obj=room,
        )
        self.call(drubase.CmdLook(), "detail", "A detail", obj=room)
        self.call(drubase.CmdLook(), "foo", "A detail", obj=room)
        room.delete()
