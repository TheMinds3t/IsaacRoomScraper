import io
import os 

settings = {
    "XPos": 200,
    "YPos": 200,
    "Width": 600,
    "Height": 400,
    "LastPath": "",
    "GUI": True,
    "BRFiles": set(),
    "RoomFiles": set()
}

set_deserialize = lambda val: set(map(lambda val2: val2.replace(";",""),val.split(";")))

cast_funcs = {
    "XPos": int,
    "YPos": int,
    "Width": int,
    "Height": int,
    "LastPath": str,
    "GUI": bool,
    "BRFiles": set_deserialize,
    "RoomFiles": set_deserialize
}

settings_file = "program_settings.ini"

def save():
    with io.open(settings_file,"w") as ex_file:
        for key in settings.keys():
            val = settings[key]
            if type(settings[key]) == set:
                val = ""
                for val2 in settings[key]:
                    if val2 != '':
                        val = f"{val2};{val}"
                    
            ex_file.write(f"{key}={val}\n")

        ex_file.flush()
        ex_file.close()

def load():
    if os.path.exists(settings_file):
        with io.open(settings_file, "r") as im_file:
            for line in im_file.readlines():
                vals = line.replace("\n","").split("=")
                settings[vals[0]] = cast_funcs[vals[0]](vals[1])

            im_file.close()