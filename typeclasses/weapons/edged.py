# -------------------------------------------------------------
#
# Weapon - object type
#
# A weapon (which here is assumed to be a bladed melee weapon for close
# combat) has three commands, stab, slash and defend. Weapons also have
# a property "magic" to determine if they are usable against certain
# enemies.
#
# Since Characters don't have special skills (yet), we let the weapon
# itself determine how easy/hard it is to hit with it, and how much
# damage it can do.
#
# -------------------------------------------------------------


import random

from evennia import CmdSet

from commands.command import Command
from typeclasses.base import Object


class CmdAttack(Command):
    """
    Attack the enemy. Commands:

      stab <enemy>
      slash <enemy>
      parry

    stab - (thrust) makes a lot of damage but is harder to hit with.
    slash - is easier to land, but does not make as much damage.
    parry - forgoes your attack but will make you harder to hit on next
            enemy attack.

    """

    # this is an example of implementing many commands as a single
    # command class, using the given command alias to separate between them.

    key = "attack"
    aliases = [
        "hit",
        "kill",
        "fight",
        "thrust",
        "pierce",
        "stab",
        "slash",
        "chop",
        "bash",
        "parry",
        "defend",
    ]
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """Implements the stab"""

        cmdstring = self.cmdstring

        if cmdstring in ("attack", "fight"):
            string = (
                "How do you want to fight? Choose one of 'stab', 'slash' or 'defend'."
            )
            self.caller.msg(string)
            return

        # parry mode
        if cmdstring in ("parry", "defend"):
            string = "You raise your weapon in a defensive pose, ready to block the next enemy attack."
            self.caller.msg(string)
            self.caller.db.combat_parry_mode = True
            self.caller.location.msg_contents(
                "%s takes a defensive stance" % self.caller, exclude=[self.caller]
            )
            return

        if not self.args:
            self.caller.msg("Who do you attack?")
            return
        target = self.caller.search(self.args.strip())
        if not target:
            return

        if cmdstring in ("thrust", "pierce", "stab"):
            hit = float(self.obj.db.hit) * 0.7  # modified due to stab
            damage = self.obj.db.damage * 2  # modified due to stab
            string = "You stab with %s. " % self.obj.key
            tstring = "%s stabs at you with %s. " % (self.caller.key, self.obj.key)
            ostring = "%s stabs at %s with %s. " % (
                self.caller.key,
                target.key,
                self.obj.key,
            )
            self.caller.db.combat_parry_mode = False
        elif cmdstring in ("slash", "chop", "bash"):
            hit = float(self.obj.db.hit)  # un modified due to slash
            damage = self.obj.db.damage  # un modified due to slash
            string = "You slash with %s. " % self.obj.key
            tstring = "%s slash at you with %s. " % (self.caller.key, self.obj.key)
            ostring = "%s slash at %s with %s. " % (
                self.caller.key,
                target.key,
                self.obj.key,
            )
            self.caller.db.combat_parry_mode = False
        else:
            self.caller.msg(
                "You fumble with your weapon, unsure of whether to stab, slash or parry ..."
            )
            self.caller.location.msg_contents(
                "%s fumbles with their weapon." % self.caller, exclude=self.caller
            )
            self.caller.db.combat_parry_mode = False
            return

        if target.db.combat_parry_mode:
            # target is defensive; even harder to hit!
            target.msg("|GYou defend, trying to avoid the attack.|n")
            hit *= 0.5

        if random.random() <= hit:
            self.caller.msg(string + "|gIt's a hit!|n")
            target.msg(tstring + "|rIt's a hit!|n")
            self.caller.location.msg_contents(
                ostring + "It's a hit!", exclude=[target, self.caller]
            )

            # call enemy hook
            if hasattr(target, "at_hit"):
                # should return True if target is defeated, False otherwise.
                target.at_hit(self.obj, self.caller, damage)
                return
            elif target.db.health:
                target.db.health -= damage
            else:
                # sorry, impossible to fight this enemy ...
                self.caller.msg("The enemy seems unaffected.")
                return
        else:
            self.caller.msg(string + "|rYou miss.|n")
            target.msg(tstring + "|gThey miss you.|n")
            self.caller.location.msg_contents(
                ostring + "They miss.", exclude=[target, self.caller]
            )


class CmdSetWeapon(CmdSet):
    """Holds the attack command."""

    def at_cmdset_creation(self):
        """called at first object creation."""
        self.add(CmdAttack())


class Weapon(Object):
    """
    This defines a bladed weapon.

    Important attributes (set at creation):
      hit - chance to hit (0-1)
      parry - chance to parry (0-1)
      damage - base damage given (modified by hit success and
               type of attack) (0-10)

    """

    def at_object_creation(self):
        """Called at first creation of the object"""
        super().at_object_creation()
        self.db.hit = 0.4  # hit chance
        self.db.parry = 0.8  # parry chance
        self.db.damage = 1.0
        self.db.magic = False
        self.cmdset.add_default(CmdSetWeapon, permanent=True)

    def reset(self):
        """
        When reset, the weapon is simply deleted, unless it has a place
        to return to.
        """
        if self.location.has_account and self.home == self.location:
            self.location.msg_contents(
                "%s suddenly and magically fades into nothingness, as if it was never there ..."
                % self.key
            )
            self.delete()
        else:
            self.location = self.home
