"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.utils import logger
from muddery.utils.builder import build_object, delete_object
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.mappings.typeclass_set import TYPECLASS
from muddery.worlddata.dao.npc_dialogues_mapper import NPC_DIALOGUES
from muddery.worlddata.dao.npc_shops_mapper import NPC_SHOPS
from muddery.utils import defines
from muddery.utils.localized_strings_handler import _


class MudderyBaseNPC(TYPECLASS("CHARACTER")):
    """
    The character not controlled by players.
    """
    typeclass_key = "BASE_NPC"
    typeclass_name = _("Base None Player Character", "typeclasses")
    model_name = "base_npcs"

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.

        """
        super(MudderyBaseNPC, self).at_object_creation()

        # NPC's shop
        if not self.attributes.has("shops"):
            self.db.shops = {}

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyBaseNPC, self).after_data_loaded()

        # Character can auto fight.
        self.auto_fight = True

        # set home
        self.home = self.location

        # load dialogues.
        self.load_dialogues()

        # load shops
        self.load_shops()

    def load_dialogues(self):
        """
        Load dialogues.
        """
        dialogues = NPC_DIALOGUES.filter(self.get_data_key())

        self.default_dialogues = [dialogue.dialogue for dialogue in dialogues if dialogue.default]
        self.dialogues = [dialogue.dialogue for dialogue in dialogues if not dialogue.default]

    def load_shops(self):
        """
        Load character's shop.
        """
        # shops records
        shop_records = NPC_SHOPS.filter(self.get_data_key())

        shop_keys = set([record.shop for record in shop_records])

        # remove old shops
        for shop_key in self.db.shops:
            if shop_key not in shop_keys:
                # remove this shop
                self.db.shops[shop_key].delete()
                del self.db.shops[shop_key]

        # add new shop
        for shop_record in shop_records:
            shop_key = shop_record.shop
            if shop_key not in self.db.shops:
                # Create shop object.
                shop_obj = build_object(shop_key)
                if not shop_obj:
                    logger.log_errmsg("Can't create shop: %s" % shop_key)
                    continue

                self.db.shops[shop_key] = shop_obj
                shop_obj.set_owner(self)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive():
            if self.dialogues or self.default_dialogues:
                # If the character have something to talk, add talk command.
                commands.append({"name": _("Talk"), "cmd": "talk", "args": self.dbref})

            # Add shops.
            for shop_obj in self.db.shops.values():
                if not shop_obj.is_visible(caller):
                    continue

                verb = shop_obj.verb
                if not verb:
                    verb = shop_obj.get_name()
                commands.append({"name": verb, "cmd": "shopping", "args": shop_obj.dbref})

            if self.friendly <= 0:
                commands.append({"name": _("Attack"), "cmd": "attack", "args": self.dbref})

        return commands

    def have_quest(self, caller):
        """
        If the npc can complete or provide quests.
        Returns (can_provide_quest, can_complete_quest).
        """
        return DIALOGUE_HANDLER.have_quest(caller, self)

    def leave_combat(self):
        """
        Leave the current combat.
        """
        status = None
        opponents = None
        if self.ndb.combat_handler:
            result = self.ndb.combat_handler.get_combat_result(self)
            if result:
                status, opponents = result

        if not self.is_temp:
            if status == defines.COMBAT_LOSE:
                self.die(opponents)

        super(MudderyBaseNPC, self).leave_combat()

        if not self.is_temp:
            if status != defines.COMBAT_LOSE:
                self.recover()
