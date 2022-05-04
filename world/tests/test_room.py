# test tutorial_world/
from evennia import create_object
from evennia.commands.default.tests import CommandTest

from typeclasses import base as drubase
from typeclasses.rooms import ticker as druticker
from typeclasses.rooms import introoutro as druintro

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

    def test_weatherroom(self):
        room = create_object(druticker.WeatherRoom, key="weatherroom")
        room.update_weather()
        druticker.TICKER_HANDLER.remove(
            # The idstring needs to match the idstring in WeatherRoom typclass.
            interval=room.db.interval, callback=room.update_weather, idstring="druidia"
        )
        room.delete()

    def test_introroom(self):
        room = create_object(druintro.IntroRoom, key="introroom")
        room.at_object_receive(self.char1, self.room1)
