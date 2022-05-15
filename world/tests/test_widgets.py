#  Test typeclasses/widgets.


from evennia import create_object
from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import mockdelay, mockdeferLater

from mock import patch
from mock.mock import MagicMock

from twisted.trial.unittest import TestCase as TwistedTestCase
from twisted.internet.base import DelayedCall

from typeclasses import base as drubase
from typeclasses.widgets import lights as drulights


DelayedCall.debug = True


class TestWidgets(TwistedTestCase, CommandTest):
    def test_baseobj(self):
        obj1 = create_object(drubase.Object, key="druobj")
        obj1.reset()
        self.assertEqual(obj1.location, obj1.home)

    @patch("typeclasses.widgets.lights.delay", mockdelay)
    @patch("evennia.scripts.taskhandler.deferLater", mockdeferLater)
    def test_lightsource(self):
        light = create_object(drulights.LightSource, key="torch", location=self.room1)
        self.call(
            drulights.CmdLight(),
            "",
            "A torch on the floor flickers and dies.|You light torch.",
            obj=light,
        )
        self.assertFalse(light.pk)
