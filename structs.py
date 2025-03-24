from PyQt6.QtGui import QImage, QColor, QPixelFormat

class Entry:
    def __init__(self, type: int, variant: int, subtype: int, weight: float = 1):
        self.ent_type = type 
        self.ent_variant = variant 
        self.ent_subtype = subtype
        self.ent_weight = weight

    def type_string(self):
        return f"{self.ent_type}.{self.ent_variant}.{self.ent_subtype}"
    
    def __str__(self):
        return f"(Type:{self.ent_type},Variant:{self.ent_variant},Subtype:{self.ent_subtype},Weight:{self.ent_weight})"
    
    def __lt__(self, other):
        return self.ent_type < other.type or (
            self.ent_type == other.type and self.ent_variant < other.variant
            ) or (self.ent_type == other.type and self.ent_variant == other.variant and self.ent_subtype < other.subtype)
    
    def __hash__(self):
        return self.ent_type * 100000 + self.ent_variant * 10000 + self.ent_subtype * 1000

    # disregard weight for comparison
    def __eq__(self, other):
        return self.ent_type == other.type and self.ent_variant == other.variant and self.ent_subtype == other.subtype

class Pos:
    def __init__(self, x:float, y:float):
        self.x = x 
        self.y = y 
    def __str__(self):
        return f"X={self.x},Y={self.y}"

class Spawn:
    def __init__(self, entry: Entry, pos: Pos):
        self.entry = entry
        self.pos = pos 
    def __str__(self):
        return f"(Spawn {self.entry} at {self.pos})"

class Door:
    def __init__(self, pos: Pos, exists: bool):
        self.pos = pos 
        self.exists = exists
    
    def __str__(self):
        return f"(Door {self.pos} (Enabled? {self.exists}))"

class Room:
    def __init__(self, entry: Entry, name: str, shape: int, difficulty: float, width: int, height: int):
        self.entry = entry
        self.shape = shape 
        self.difficulty = difficulty 
        self.name = name 
        self.width = width 
        self.height = height 
        self.spawns = list()
        self.doors = list()

    def add_spawn(self, spawn: Spawn):
        self.spawns.append(spawn)

    def add_door(self, door: Door):
        self.doors.append(door)

    def __str__(self):
        return f"(Room \'{self.name}\' {self.entry}, Shape={self.shape} Dimensions=({self.width},{self.height}) Difficulty={self.difficulty}, Doors={list(map(lambda val: str(val), self.doors))}, Spawns={list(map(lambda val: str(val), self.spawns))})"
    

def add_outline_to_img(img: QImage):
    if not img.allGray() and img.pixelFormat().colorModel() == QPixelFormat.ColorModel.RGB:
        for x_p in range(0,img.width()):
            for y_p in range(0,img.height()):
                col = img.pixelColor(x_p,y_p)
                av = (col.red() + col.green() + col.blue()) / 3.0

                if col.alpha() >= 15 and col.alpha() != 100 and av > 30: # border color
                    for i in range(-2,3):
                        for j in range(-2,3):
                            prox_x = max(min(x_p+i,img.width()-1),0)
                            prox_y = max(min(y_p+j,img.height()-1),0)
                            prox_col = img.pixelColor(prox_x,prox_y)

                            if prox_col.alpha() == 0 and prox_x != x_p and prox_y != y_p:
                                img.setPixelColor(prox_x, prox_y, QColor(0,0,0,100))
    
    return img 

class BREntry:
    def __init__(self, id: int, variant: int, subtype: int, name: str = None, group: str = None, kind: str = None, image: str = None, ):
        self.group = group
        self.kind = kind 
        self.entry = Entry(id, variant, subtype)
        self.name = name 
        self.image = None
        # self.image = add_outline_to_img(QImage(image))
        self.image_path = image 

    def __eq__(self, other):
        return other != None and self.entry == other.entry