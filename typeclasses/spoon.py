# mygame/typeclasses/spoon.py

from typeclasses.objects import Object

class Spoon(Object):
    """
    This creates a simple spoon object
    """
    def at_object_creation(self):
        "this is called only once, when object is first created"
        # add a persistent attribute 'desc'
        # to object (silly example).
        self.db.desc = "There is no spoon."
