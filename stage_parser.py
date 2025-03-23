import easygui
import structs
import config
import os
from bs4 import BeautifulSoup

basement_renovator_dictionary = {}

def pass_or_find_file(filename:str, msg:str = "Open the xml version of STB files, or the EntitiesMod.xml/EntitiesRepentance.xml", multiple:bool = False):
    if filename == None:
        return easygui.fileopenbox(msg=msg, 
                               title="Selecting Stage File/Basement Renovator Registry", 
                               filetypes=["*.xml"], multiple=multiple)
    
    return filename
    
def scrape_br_file(filename: str = None):
    old_total = len(basement_renovator_dictionary)
    filename = pass_or_find_file(filename, "Open the EntitiesMod.xml/EntitiesRepentance.xml file from Basement Renovator")

    # in case file selection is canceled validate once more
    if filename != None and os.path.exists(filename):
        with open(filename, 'r') as file:
            config.settings["BRFiles"].add(filename)
            reg_file = BeautifulSoup(file.read(), "xml")

            for ent in reg_file.find('data').find_all('entity'):
                if ent:
                    br_entry = structs.BREntry(group=ent.get("Group"),kind=ent.get("Kind"), image=f"{os.path.dirname(filename)}/{ent.get("Image")}",id=ent.get("ID"),variant=ent.get("Variant"),subtype=ent.get("Subtype"),name=ent.get("Name"))
                    basement_renovator_dictionary[br_entry.entry.type_string()] = br_entry

            config.save()
    
    print(f"Pre-scrape size: {old_total}, Post-scrape size: {len(basement_renovator_dictionary)}!")

def parse_stage(filename: str = None):
    ret_rooms = list()

    filename = pass_or_find_file(filename, "Open the xml version of STB files")
    
    # in case file selection is canceled validate once more
    if filename != None and os.path.exists(filename): 
        with open(filename, 'r') as file:
            print(f"Parsing \'{filename}\' stage file contents...")
            stage_file = BeautifulSoup(file.read(), "xml")

            for room in stage_file.find_all('room'): 
                if room:
                    room_obj = structs.Room(entry=structs.Entry(type=room.get('type'),
                                                                variant=room.get('variant'),
                                                                subtype=room.get("subtype"),
                                                                weight=room.get('weight')),
                                            name=room.get('name'),
                                            shape=room.get('shape'),
                                            width=room.get('width'),
                                            height=room.get('height'),
                                            difficulty=room.get('difficulty'))
                    
                    for room_entry in room.children:
                        if room_entry.name == 'spawn':
                            pos = structs.Pos(room_entry.get('x'), room_entry.get('y'))
                            room_entry = room_entry.find('entity')
                            
                            room_obj.add_spawn(structs.Spawn(pos=pos, 
                                                            entry=structs.Entry(type=room_entry.get('type'),
                                                                                variant=room_entry.get('variant'),
                                                                                subtype=room_entry.get("subtype"),
                                                                                weight=room_entry.get('weight'))))
                        elif room_entry.name == 'door':
                            room_obj.add_door(structs.Door(pos=structs.Pos(room_entry.get('x'), room_entry.get('y')), 
                                                        exists=room_entry.get('exists')))
                    
                    ret_rooms.append(room_obj)

            # Using find() to extract attributes 
            # of the first instance of the tag
            # b_name = roomlist.find('child', {'name':'Frank'})
        
        config.save()
    
    return ret_rooms

