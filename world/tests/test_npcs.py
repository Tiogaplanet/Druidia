# test the NPCs.
from evennia import create_object
from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import EvenniaTest

from typeclasses.npcs import mob as drumob


class TestMob(EvenniaTest):
    def test_mob(self):
        mobobj = create_object(drumob.Mob, key="mob")
        self.assertEqual(mobobj.db.is_dead, True)
        mobobj.set_alive()
        self.assertEqual(mobobj.db.is_dead, False)
        mobobj.set_dead()
        self.assertEqual(mobobj.db.is_dead, True)
        mobobj._set_ticker(0, "foo", stop=True)
        # TODO should be expanded with further tests of the modes and damage etc.
