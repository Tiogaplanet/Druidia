"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter


class Character(DefaultCharacter, Object):
    """
    This is a character class that has poses, sdesc and recog.
        The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    # Handlers
    @lazy_property
    def sdesc(self):
        return SdescHandler(self)

    @lazy_property
    def recog(self):
        return RecogHandler(self)

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.
        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.
        Keyword Args:
            pose (bool): Include the pose (if available) in the return.
        Returns:
            name (str): A string of the sdesc containing the name of the object,
            if this is defined.
                including the DBREF if this user is privileged to control
                said object.
        Notes:
            The RPCharacter version of this method colors its display to make
            characters stand out from other objects.
        """
        idstr = "(#%s)" % self.id if self.access(looker, access_type="control") else ""
        if looker == self:
            sdesc = self.key
        else:
            try:
                recog = looker.recog.get(self)
            except AttributeError:
                recog = None
            sdesc = recog or (hasattr(self, "sdesc") and self.sdesc.get()) or self.key
        pose = " %s" % (self.db.pose or "is here.") if kwargs.get("pose", False) else ""
        return "|c%s|n%s%s" % (sdesc, idstr, pose)

    def at_object_creation(self):
        """
        Called at initial creation.
        """
        super().at_object_creation()

        self.db._sdesc = ""
        self.db._sdesc_regex = ""

        self.db._recog_ref2recog = {}
        self.db._recog_obj2regex = {}
        self.db._recog_obj2recog = {}

        self.cmdset.add(RPSystemCmdSet, permanent=True)
        # initializing sdesc
        self.sdesc.add("A normal person")

    def at_before_say(self, message, **kwargs):
        """
        Called before the object says or whispers anything, return modified message.
        Args:
            message (str): The suggested say/whisper text spoken by self.
        Keyword Args:
            whisper (bool): If True, this is a whisper rather than a say.
        """
        if kwargs.get("whisper"):
            return f'/me whispers "{message}"'
        return f'/me says, "{message}"'

    def process_sdesc(self, sdesc, obj, **kwargs):
        """
        Allows to customize how your sdesc is displayed (primarily by
        changing colors).
        Args:
            sdesc (str): The sdesc to display.
            obj (Object): The object to which the adjoining sdesc
                belongs. If this object is equal to yourself, then
                you are viewing yourself (and sdesc is your key).
                This is not used by default.
        Returns:
            sdesc (str): The processed sdesc ready
                for display.
        """
        return "|b%s|n" % sdesc

    def process_recog(self, recog, obj, **kwargs):
        """
        Allows to customize how a recog string is displayed.
        Args:
            recog (str): The recog string. It has already been
                translated from the original sdesc at this point.
            obj (Object): The object the recog:ed string belongs to.
                This is not used by default.
        Returns:
            recog (str): The modified recog string.
        """
        return self.process_sdesc(recog, obj)

    def process_language(self, text, speaker, language, **kwargs):
        """
        Allows to process the spoken text, for example
        by obfuscating language based on your and the
        speaker's language skills. Also a good place to
        put coloring.
        Args:
            text (str): The text to process.
            speaker (Object): The object delivering the text.
            language (str): An identifier string for the language.
        Return:
            text (str): The optionally processed text.
        Notes:
            This is designed to work together with a string obfuscator
            such as the `obfuscate_language` or `obfuscate_whisper` in
            the evennia.contrib.rplanguage module.
        """
        return "%s|w%s|n" % ("|W(%s)" % language if language else "", text)
