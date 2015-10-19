"""
Room

Rooms are simple containers that has no location of their own.

"""

import traceback
from django.conf import settings
from muddery.typeclasses.objects import MudderyObject
from muddery.utils import script_handler
from evennia.objects.objects import DefaultRoom


class MudderyRoom(MudderyObject, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def at_object_receive(self, moved_obj, source_location):
        """
        Called after an object has been moved into this object.
        
        Args:
        moved_obj (Object): The object moved into this one
        source_location (Object): Where `moved_object` came from.
        
        """
        super(MudderyRoom, self).at_object_receive(moved_obj, source_location)

        if not settings.SOLO_MODE:
            # send surrounding changes to player
            type = self.get_surrounding_type(moved_obj)
            if type:
                change = {type: [{"dbref": moved_obj.dbref,
                                  "name": moved_obj.get_name()}]}
                self.msg_contents({"obj_moved_in": change}, exclude=moved_obj)

        # trigger event
        if moved_obj.has_player:
            self.event.at_character_move_in(moved_obj)


    def at_object_left(self, moved_obj, target_location):
        """
        Called after an object has been removed from this object.
        
        Args:
        moved_obj (Object): The object leaving
        target_location (Object): Where `moved_obj` is going.
        
        """
        super(MudderyRoom, self).at_object_left(moved_obj, target_location)

        if not settings.SOLO_MODE:
            # send surrounding changes to player
            type = self.get_surrounding_type(moved_obj)
            if type:
                change = {type: [{"dbref": moved_obj.dbref,
                                  "name": moved_obj.get_name()}]}
                self.msg_contents({"obj_moved_out": change}, exclude=moved_obj)


    def get_surroundings(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
            
        # get name, description, commands and all objects in it
        info = {"exits": [],
                "npcs": [],
                "things": [],
                "players": [],
                "offlines": []}

        visible = (cont for cont in self.contents if cont != caller and
                   cont.access(caller, "view"))

        if settings.SOLO_MODE:
            visible = (cont for cont in visible if not cont.has_player)

        for cont in visible:
            # only show objects that match the condition
            if hasattr(cont, "condition"):
                if not script_handler.match_condition(caller, cont.condition):
                    continue
                        
            type = self.get_surrounding_type(cont)
            if type:
                appearance = {}

                if type == "npcs":
                    # add quest status
                    provide_quest, finish_quest = cont.have_quest(caller)
                    appearance["provide_quest"] = provide_quest
                    appearance["finish_quest"] = finish_quest

                appearance["dbref"] = cont.dbref
                appearance["name"] = cont.get_name()
                
                info[type].append(appearance)

        return info


    def get_surrounding_type(self, obj):
        """
        Get surrounding's view type.
        """
        if obj.destination:
            return "exits"
        elif obj.is_typeclass(settings.BASE_CHARACTER_TYPECLASS, exact=False):
            if obj.has_player:
                return "players"
            else:
                return "offlines"
        elif obj.is_typeclass(settings.BASE_NPC_TYPECLASS, exact=False):
            return "npcs"
        else:
            return "things"
