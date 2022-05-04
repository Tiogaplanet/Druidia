# Test Druidia's rooms.
from evennia import create_object
from evennia.commands.default.tests import CommandTest

from typeclasses import base as drubase
from typeclasses.rooms import ticker as druticker
from typeclasses.rooms import introoutro as druintro
from typeclasses.rooms import dark as drudark
from typeclasses.rooms import teleports as drutele


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
            interval=room.db.interval,
            callback=room.update_weather,
            idstring="druidia",
        )
        room.delete()

    def test_introroom(self):
        room = create_object(druintro.IntroRoom, key="introroom")
        room.at_object_receive(self.char1, self.room1)

    def test_bridgeroom(self):
        room = create_object(druticker.BridgeRoom, key="bridgeroom")
        room.update_weather()
        self.char1.move_to(room)
        self.call(
            druticker.CmdBridgeHelp(),
            "",
            "You are trying hard not to fall off the bridge ...",
            obj=room,
        )
        self.call(
            druticker.CmdLookBridge(),
            "",
            "bridgeroom\nYou are standing very close to the the bridge's western foundation.",
            obj=room,
        )
        room.at_object_leave(self.char1, self.room1)
        druticker.TICKER_HANDLER.remove(
            interval=room.db.interval, callback=room.update_weather, idstring="druidia"
        )
        room.delete()

    def test_darkroom(self):
        room = create_object(drudark.DarkRoom, key="darkroom")
        self.char1.move_to(room)
        self.call(drudark.CmdDarkHelp(), "", "Can't help you until")

    def test_teleportroom(self):
        create_object(drutele.TeleportRoom, key="teleportroom")

    def test_outroroom(self):
        create_object(druintro.OutroRoom, key="outroroom")
