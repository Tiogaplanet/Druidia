#  Test typeclasses/exits.


from mock import patch

from evennia import create_object
from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import mockdelay, mockdeferLater

from twisted.trial.unittest import TestCase as TwistedTestCase
from twisted.internet.base import DelayedCall

from typeclasses.exits import crumblingwall as drucrumblingwall


DelayedCall.debug = True


class TestExits(TwistedTestCase, CommandTest):
    @patch("typeclasses.exits.crumblingwall.delay", mockdelay)
    @patch("evennia.scripts.taskhandler.deferLater", mockdeferLater)
    def test_crumblingwall(self):
        wall = create_object(drucrumblingwall.CrumblingWall, key="wall", location=self.room1)
        wall.db.destination = self.room2.dbref
        self.assertFalse(wall.db.button_exposed)
        self.assertFalse(wall.db.exit_open)
        wall.db.root_pos = {"yellow": 0, "green": 0, "red": 0, "blue": 0}
        self.call(
            drucrumblingwall.CmdShiftRoot(),
            "blue root right",
            "You shove the root adorned with small blue flowers to the right.",
            obj=wall,
        )
        self.call(
            drucrumblingwall.CmdShiftRoot(),
            "red root left",
            "You shift the reddish root to the left.",
            obj=wall,
        )
        self.call(
            drucrumblingwall.CmdShiftRoot(),
            "yellow root down",
            "You shove the root adorned with small yellow flowers downwards.",
            obj=wall,
        )
        self.call(
            drucrumblingwall.CmdShiftRoot(),
            "green root up",
            "You shift the weedy green root upwards.|Holding aside the root you think you notice something behind it ...",
            obj=wall,
        )
        self.call(
            drucrumblingwall.CmdPressButton(),
            "",
            "You move your fingers over the suspicious depression, then gives it a decisive push. First",
            obj=wall,
        )
        # we patch out the delay, so these are closed immediately
        self.assertFalse(wall.db.button_exposed)
        self.assertFalse(wall.db.exit_open)
