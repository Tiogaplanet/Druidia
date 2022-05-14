#  Test weapons (and weapon racks).


from evennia import create_object
from evennia.commands.default.tests import CommandTest

from typeclasses.weapons import edged as druedged
from typeclasses.weapons import rack as drurack
from twisted.trial.unittest import TestCase as TwistedTestCase


class TestWeapons(TwistedTestCase, CommandTest):
    def test_weapon(self):
        weapon = create_object(druedged.Weapon, key="sword", location=self.char1)
        self.call(
            druedged.CmdAttack(), "Char", "You stab with sword.", obj=weapon, cmdstring="stab"
        )
        self.call(
            druedged.CmdAttack(), "Char", "You slash with sword.", obj=weapon, cmdstring="slash"
        )

    def test_weaponrack(self):
        rack = create_object(drurack.WeaponRack, key="rack", location=self.room1)
        rack.db.available_weapons = ["sword"]
        self.call(drurack.CmdGetWeapon(), "", "You find Rusty sword.", obj=rack)
