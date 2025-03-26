import stage_parser
import gui
import config
import sys
import os 

def execute():
    config.load()

    for br_file in config.settings["BRFiles"]:
        if os.path.exists(br_file):
            print(f"Preloading \'{br_file}\' as a Basement Renovator Entity XML!")
            stage_parser.scrape_br_file(br_file)

    cmd_rooms = list()

    for i in range(1,len(sys.argv)):
        if os.path.exists(os.path.dirname(sys.argv[i])):
            cmd_rooms.append(sys.argv[i])

    # TODO: figure out why there are floating QEntityTiles generated from loading existing files 
    # for file in config.settings["RoomFiles"]:
    #     if len(file) > 0 and os.path.exists(file):
    #         cmd_rooms.append(file)

    cur_gui = gui.MainGUI(cmd_rooms)

    result = cur_gui.app.exec()
    config.save()
    sys.exit(result)

if __name__ == "__main__":
    execute()