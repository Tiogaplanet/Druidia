#  test tutorial_world/objects


from evennia import create_object
from evennia.commands.default.tests import CommandTest

from typeclasses.scenery import readable as drureadable
from typeclasses.scenery import climbable as druclimbable
from typeclasses.scenery import sculptures as drusculptures
from mock.mock import MagicMock
from twisted.trial.unittest import TestCase as TwistedTestCase

from twisted.internet.base import DelayedCall

DelayedCall.debug = True


class TestScenery(TwistedTestCase, CommandTest):
    def test_readable(self):
        readable = create_object(drureadable.Readable, key="book", location=self.room1)
        readable.db.readable_text = "Text to read"
        self.call(drureadable.CmdRead(), "book", "You read book:\n  Text to read", obj=readable)

    def test_climbable(self):
        climbable = create_object(druclimbable.Climbable, key="tree", location=self.room1)
        self.call(
            druclimbable.CmdClimb(),
            "tree",
            "You climb tree. Having looked around, you climb down again.",
            obj=climbable,
        )
        self.assertEqual(
            self.char1.tags.get("climbed_tree", category="world"),
            "climbed_tree",
        )

    def test_obelisk(self):
        obelisk = create_object(drusculptures.Obelisk, key="obelisk", location=self.room1)
        self.assertEqual(obelisk.return_appearance(self.char1).startswith("|cobelisk("), True)
