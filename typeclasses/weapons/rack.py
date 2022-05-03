# -------------------------------------------------------------
#
# Weapon rack - spawns weapons
#
# This is a spawner mechanism that creates custom weapons from a
# spawner prototype dictionary. Note that we only create a single typeclass
# (Weapon) yet customize all these different weapons using the spawner.
# The spawner dictionaries could easily sit in separate modules and be
# used to create unique and interesting variations of typeclassed
# objects.
#
# -------------------------------------------------------------


from evennia import CmdSet

from commands.command import Command
from typeclasses.base import Object
from typeclasses.weapons.edged import Weapon

WEAPON_PROTOTYPES = {
    "weapon": {
        "typeclass": "typeclasses.weapons.edged.Weapon",
        "key": "Weapon",
        "hit": 0.2,
        "parry": 0.2,
        "damage": 1.0,
        "magic": False,
        "desc": "A generic blade.",
    },
    "knife": {
        "prototype_parent": "weapon",
        "aliases": "sword",
        "key": "Kitchen knife",
        "desc": "A rusty kitchen knife. Better than nothing.",
        "damage": 3,
    },
    "dagger": {
        "prototype_parent": "knife",
        "key": "Rusty dagger",
        "aliases": ["knife", "dagger"],
        "desc": "A double-edged dagger with a nicked edge and a wooden handle.",
        "hit": 0.25,
    },
    "sword": {
        "prototype_parent": "weapon",
        "key": "Rusty sword",
        "aliases": ["sword"],
        "desc": "A rusty shortsword. It has a leather-wrapped handle covered i food grease.",
        "hit": 0.3,
        "damage": 5,
        "parry": 0.5,
    },
    "club": {
        "prototype_parent": "weapon",
        "key": "Club",
        "desc": "A heavy wooden club, little more than a heavy branch.",
        "hit": 0.4,
        "damage": 6,
        "parry": 0.2,
    },
    "axe": {
        "prototype_parent": "weapon",
        "key": "Axe",
        "desc": "A woodcutter's axe with a keen edge.",
        "hit": 0.4,
        "damage": 6,
        "parry": 0.2,
    },
    "ornate longsword": {
        "prototype_parent": "sword",
        "key": "Ornate longsword",
        "desc": "A fine longsword with some swirling patterns on the handle.",
        "hit": 0.5,
        "magic": True,
        "damage": 5,
    },
    "warhammer": {
        "prototype_parent": "club",
        "key": "Silver Warhammer",
        "aliases": ["hammer", "warhammer", "war"],
        "desc": "A heavy war hammer with silver ornaments. This huge weapon causes massive damage - if you can hit.",
        "hit": 0.4,
        "magic": True,
        "damage": 8,
    },
    "rune axe": {
        "prototype_parent": "axe",
        "key": "Runeaxe",
        "aliases": ["axe"],
        "hit": 0.4,
        "magic": True,
        "damage": 6,
    },
    "thruning": {
        "prototype_parent": "ornate longsword",
        "key": "Broadsword named Thruning",
        "desc": "This heavy bladed weapon is marked with the name 'Thruning'. It is very powerful in skilled hands.",
        "hit": 0.6,
        "parry": 0.6,
        "damage": 7,
    },
    "slayer waraxe": {
        "prototype_parent": "rune axe",
        "key": "Slayer waraxe",
        "aliases": ["waraxe", "war", "slayer"],
        "desc": "A huge double-bladed axe marked with the runes for 'Slayer'."
        " It has more runic inscriptions on its head, which you cannot decipher.",
        "hit": 0.7,
        "damage": 8,
    },
    "ghostblade": {
        "prototype_parent": "ornate longsword",
        "key": "The Ghostblade",
        "aliases": ["blade", "ghost"],
        "desc": "This massive sword is large as you are tall, yet seems to weigh almost nothing."
        " It's almost like it's not really there.",
        "hit": 0.9,
        "parry": 0.8,
        "damage": 10,
    },
    "hawkblade": {
        "prototype_parent": "ghostblade",
        "key": "The Hawkblade",
        "aliases": ["hawk", "blade"],
        "desc": "The weapon of a long-dead heroine and a more civilized age,"
        " the hawk-shaped hilt of this blade almost has a life of its own.",
        "hit": 0.85,
        "parry": 0.7,
        "damage": 11,
    },
}


class CmdGetWeapon(Command):
    """
    Usage:
      get weapon

    This will try to obtain a weapon from the container.
    """

    key = "get weapon"
    aliases = "get weapon"
    locks = "cmd:all()"
    help_category = "World"

    def func(self):
        """
        Get a weapon from the container. It will
        itself handle all messages.
        """
        self.obj.produce_weapon(self.caller)


class CmdSetWeaponRack(CmdSet):
    """
    The cmdset for the rack.
    """

    key = "weaponrack_cmdset"

    def at_cmdset_creation(self):
        """Called at first creation of cmdset"""
        self.add(CmdGetWeapon())


class WeaponRack(Object):
    """
    This object represents a weapon store. When people use the
    "get weapon" command on this rack, it will produce one
    random weapon from among those registered to exist
    on it. This will also set a property on the character
    to make sure they can't get more than one at a time.

    Attributes to set on this object:
        available_weapons: list of prototype-keys from
            WEAPON_PROTOTYPES, the weapons available in this rack.
        no_more_weapons_msg - error message to return to accounts
            who already got one weapon from the rack and tries to
            grab another one.

    """

    def at_object_creation(self):
        """
        called at creation
        """
        self.cmdset.add_default(CmdSetWeaponRack, permanent=True)
        self.db.rack_id = "weaponrack_1"
        # these are prototype names from the prototype
        # dictionary above.
        self.db.get_weapon_msg = dedent(
            """
            You find |c%s|n. While carrying this weapon, these actions are available:
              |wstab/thrust/pierce <target>|n - poke at the enemy. More damage but harder to hit.
              |wslash/chop/bash <target>|n - swipe at the enemy. Less damage but easier to hit.
              |wdefend/parry|n - protect yourself and make yourself harder to hit.)
            """
        ).strip()

        self.db.no_more_weapons_msg = "you find nothing else of use."
        self.db.available_weapons = ["knife", "dagger", "sword", "club"]

    def produce_weapon(self, caller):
        """
        This will produce a new weapon from the rack,
        assuming the caller hasn't already gotten one. When
        doing so, the caller will get Tagged with the id
        of this rack, to make sure they cannot keep
        pulling weapons from it indefinitely.
        """
        rack_id = self.db.rack_id
        if caller.tags.get(rack_id, category="world"):
            caller.msg(self.db.no_more_weapons_msg)
        else:
            prototype = random.choice(self.db.available_weapons)
            # use the spawner to create a new Weapon from the
            # spawner dictionary, tag the caller
            wpn = spawn(
                WEAPON_PROTOTYPES[prototype], prototype_parents=WEAPON_PROTOTYPES
            )[0]
            caller.tags.add(rack_id, category="world")
            wpn.location = caller
            caller.msg(self.db.get_weapon_msg % wpn.key)
