"""

Base Object typeclass.

This module holds all base Object typeclass.  All objects in Druidia
descend from this typeclass.

"""


from evennia import DefaultObject


# -------------------------------------------------------------
#
# Object
#
# The Object is the base class for all items
# in Druidia.
#
# Objects may also be "reset". What the reset means
# is up to the object. It can be the resetting of the world
# itself, or the removal of an inventory item from a
# character's inventory when leaving Druidia, for example.
#
# -------------------------------------------------------------

class Object(DefaultObject):
    """
    This is the baseclass for all objects in Druidia.
    """

    def at_object_creation(self):
        """Called when the object is first created."""
        super().at_object_creation()

    def reset(self):
        """Resets the object, whatever that may mean."""
        self.location = self.home
