import stage_parser
import gui
import config
import sys
import os 

if __name__ == "__main__":
    config.load()

    for br_file in config.settings["BRFiles"]:
        if os.path.exists(br_file):
            print(f"Preloading \'{br_file}\' as a Basement Renovator Entity XML!")
            stage_parser.scrape_br_file(br_file)

    cmd_rooms = list()

    for i in range(1,len(sys.argv)):
        if os.path.exists(os.path.dirname(sys.argv[i])):
            cmd_rooms.append(stage_parser.parse_stage(sys.argv[i]))

    gui = gui.MainGUI(cmd_rooms)

    result = gui.app.exec()
    config.save()
    sys.exit(result)