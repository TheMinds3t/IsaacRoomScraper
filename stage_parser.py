import easygui
import structs
import config
import os
from bs4 import BeautifulSoup, Tag, ResultSet
from PyQt6.QtGui import QImage, QColor, QPixelFormat

basement_renovator_dictionary = dict[str,structs.BREntry]()
br_group_to_kind_map = dict[str,str]()

loaded_files = list[str]()

def unload_file(filename:str):
    for file in loaded_files:
        if file == filename:
            loaded_files.remove(file)
            return True 
        
    return False 

def pass_or_find_file(filename:str, msg:str = "Open the xml version of STB files, or the EntitiesMod.xml/EntitiesRepentance.xml", multiple:bool = False):
    if filename == None:
        path = f"{config.settings["LastPath"]}/"
        if not os.path.exists(path):
            path = "*"

        file_chosen = easygui.fileopenbox(msg=msg, 
                               title="Selecting Stage File/Basement Renovator Registry", default=path,
                               filetypes=["*.xml"], multiple=multiple)
        
        if file_chosen != None:
            if type(file_chosen) == list:
                config.settings["LastPath"] = os.path.dirname(file_chosen[-1])
                config.save()
                return file_chosen                    
            elif os.path.exists(file_chosen):
                config.settings["LastPath"] = os.path.dirname(file_chosen)
                config.save()
                return file_chosen
    
    if multiple:
        ret = list()
        ret.append(filename)
        return ret
    else:
        return filename

def flush_floor_group_kind_dict(queue:ResultSet):
    while len(queue) > 0:
        cur = queue[0]
        if isinstance(cur, Tag):
            if "Label" in cur.attrs and "Name" in cur.attrs:
                # print(f"adding {cur["Name"]} = {cur["Label"]} to floor dict")
                br_group_to_kind_map[cur["Name"]] = cur["Label"]
            elif "Label" in cur.attrs:
                for child in cur.children:
                    if isinstance(child, Tag) and child.name == "group" and "Name" in child.attrs:
                        br_group_to_kind_map[child["Name"]] = cur["Label"]
            else:
                pass
                # print(f"not adding {cur.get("Name")} = {cur.get("Label")} to floor dict")
        else:
            pass
            # print(f"{cur} is not a valid tag while flushing floor dict..")

        queue.pop(0)
    
def scrape_br_file(filename: str = None):
    old_total = len(basement_renovator_dictionary)
    filename = pass_or_find_file(filename=filename, msg="Open the EntitiesMod.xml/EntitiesRepentance.xml file from Basement Renovator")
    
    # in case file selection is canceled validate once more
    if filename != None and os.path.exists(filename):
        with open(filename, 'r') as file:
            config.settings["BRFiles"].add(filename)
            reg_file = BeautifulSoup(file.read(), "xml")
            floor_group_layout = reg_file.find_all(name="group")

            if floor_group_layout:
                print(f"Adding floormap for {filename}:")
                flush_floor_group_kind_dict(floor_group_layout)

            for ent in reg_file.find('data').find_all('entity'):
                if ent and "ID" in ent.attrs and "Variant" in ent.attrs:
                    group = ent.get("Group")
                    kind = ent.get("Kind")

                    if group == None and ent.parent.name == "group":
                        if "Label" in ent.parent.attrs or "Name" in ent.parent.attrs:
                            kind = ent.parent.get("Label")                        
                            group = ent.parent.get("Name")
                        else:
                            cur_parent = ent.parent 

                            while cur_parent.name == "group":
                                if "Name" in cur_parent.attrs:
                                    group = cur_parent["Name"]
                                if "Label" in cur_parent.attrs:
                                    kind = cur_parent["Label"]

                                cur_parent = cur_parent.parent 

                                if cur_parent.parent.name != "group":
                                    break

                    if kind == None and group != None and group in br_group_to_kind_map:
                        kind = br_group_to_kind_map[group]

                    if group == None and kind != None and kind in br_group_to_kind_map:
                        group = br_group_to_kind_map[kind]

                    if ent.parent.name == "group" and "Label" in ent.parent.attrs:
                        kind = ent.parent["Label"]

                    br_entry = structs.BREntry(group=group,kind=kind, image=f"{os.path.dirname(filename)}/{ent.get("Image")}",id=ent.get("ID"),variant=ent.get("Variant"),subtype=ent.get("Subtype"),name=ent.get("Name"))
                    basement_renovator_dictionary.setdefault(br_entry.entry.type_string(), br_entry)

            config.save()
    
    print(f"Pre-scrape size: {old_total}, Post-scrape size: {len(basement_renovator_dictionary)}!")

def get_br_entry(entry: structs.Entry) -> structs.BREntry:
    ret = basement_renovator_dictionary.get(entry.type_string())

    if ret != None:
        if ret.image == None:
            ret.image = structs.add_outline_to_img(QImage(ret.image_path))
        
        return ret

def parse_stage(filename: str = None):
    ret_rooms = list()

    filenames = pass_or_find_file(filename, "Open the xml version of STB files", True)
    
    for filename in filenames:
        # in case file selection is canceled validate once more
        if filename != None and os.path.exists(filename): 
            try:
                with open(filename, 'r') as file:
                    print(f"Parsing \'{filename}\' stage file contents...")
                    stage_file = BeautifulSoup(file.read(), "xml")
                    rooms = stage_file.find_all('room')
                    config.settings["RoomFiles"].add(filename)
                    
                    if len(rooms) > 0:
                        loaded_files.append(filename)

                        for room in rooms: 
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
            except PermissionError:
                print(f"Unable to read \'{filename}\', program lacks sufficient permissions!")
                config.save()
    
    return ret_rooms, filenames

