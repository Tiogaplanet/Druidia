# mygame/typeclasses/flowers.py

from typeclasses.objects import Object

class Rose(Object):
    """
    This creates a simple rose object
    """
    def at_object_creation(self):
        "this is called only once, when object is first created"
        # add a persistent attribute 'desc'
        # to object (silly example).
        self.db.desc = "This is a pretty rose with thorns."
