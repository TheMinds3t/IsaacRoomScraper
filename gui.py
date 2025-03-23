import PyQt6.QtGui
import PyQt6.Qt6
import structs 
import stage_parser 
import config
import math

# import PyQt6.QtWidgets as qt
from PyQt6.QtWidgets import QVBoxLayout, QApplication, QLabel, QWidget, QPushButton, QScrollArea, QGridLayout, QVBoxLayout
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QImage, QPixmap, QColor


class QEntityTile(QWidget):
    def __init__(self, entry: structs.Entry, parent: QWidget):
        super().__init__(parent=parent)
        self.entry = entry 
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMaximumSize(128,160)
        self.id_label = QLabel(self.entry.type_string())
        self.setFixedSize(128,96)

        if stage_parser.basement_renovator_dictionary.get(self.entry.type_string()):
            ent_info = stage_parser.basement_renovator_dictionary[self.entry.type_string()]
            self.img = QImage(ent_info.image)
            self.img_label = QLabel()
            self.img_label.setPixmap(QPixmap(self.img))
            self.setFixedSize(max(math.floor(self.img.width()*2),128),max(math.floor(self.img.height()*1.5)+64,96))
            self.layout.addWidget(self.img_label)
            self.id_label.setText(f"{ent_info.name}\n{self.entry.type_string()}")

        self.layout.addWidget(self.id_label)
        self.quantity_label = QLabel("Quantity: 1")
        self.layout.addWidget(self.quantity_label)
        self.quantity = 1

    def increment_quantity(self):
        self.quantity += 1
        self.quantity_label.setText(f"Quantity: {self.quantity}")

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QtGui.QPainter(self)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(rect)

class MainGUI:
    def __init__(self, rooms: list):
        self.app = QApplication([])

        self.window = QWidget()
        self.window.setWindowTitle("Isaac Room Statistics")
        self.window.setGeometry(200, 200, config.settings["Width"], config.settings["Height"])
        self.layout = QGridLayout(parent=self.window)
        self.layout.setColumnMinimumWidth(1,96)
        self.layout.setColumnMinimumWidth(3,96)
        self.layout.setRowMinimumHeight(1,24)
        self.layout.setRowMinimumHeight(2,24)
        self.layout.setRowMinimumHeight(3,48)
        self.window.setLayout(self.layout)

        self.ent_tile_scroll_area = QScrollArea()
        self.ent_tile_layout = QGridLayout(self.ent_tile_scroll_area)
        self.ent_tile_layout.setSpacing(64)
        self.ent_tile_layout.setContentsMargins(20,20,20,20)

        self.ent_tile_area = QWidget()
        self.ent_tile_area.setLayout(self.ent_tile_layout)
        self.ent_tile_scroll_area.setWidgetResizable(True)
        self.ent_tile_scroll_area.setMinimumWidth(200)
        self.ent_tile_scroll_area.setLayout(self.ent_tile_layout)
        self.ent_tile_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ent_tile_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ent_tile_scroll_area.setWidget(self.ent_tile_area)
        
        self.layout.addWidget(self.ent_tile_scroll_area,1,3,4,4)

        self.add_room_button = QPushButton(text="Add Stage Roomlist XML",parent=self.window)
        self.add_room_button.clicked.connect(self.prompt_for_room)
        self.layout.addWidget(self.add_room_button,1,1,1,2)
        self.add_br_button = QPushButton(text="Add Basement Renovator Entity XMLs For Images",parent=self.window)
        self.add_br_button.clicked.connect(self.prompt_for_br)
        self.layout.addWidget(self.add_br_button,2,1,1,2)
        self.cur_entity_tiles = {}
        self.loaded_rooms = list()
        self.window.show()

    def prompt_for_room(self):
        for room in stage_parser.parse_stage():
            self.add_room(room)

    def prompt_for_br(self):
        stage_parser.scrape_br_file()
        self.window.repaint()

    def add_room(self, room: structs.Room):
        for spawn in room.spawns:
            new_tile = QEntityTile(parent=self.ent_tile_area,entry=spawn.entry)

            if spawn.entry.type_string() in self.cur_entity_tiles.keys():
                self.cur_entity_tiles[spawn.entry.type_string()].increment_quantity()
            else:
                x_ind = math.ceil((len(self.cur_entity_tiles)+1) / 4) - 1
                y_ind = len(self.cur_entity_tiles) % 4
                self.ent_tile_layout.addWidget(new_tile, x_ind, y_ind)
                self.ent_tile_layout.update()
                self.ent_tile_layout.setGeometry(QtCore.QRect(0,0,200,(math.ceil(len(self.cur_entity_tiles) / 4) + 1) * 128))
                self.cur_entity_tiles[spawn.entry.type_string()] = new_tile
    
        self.loaded_rooms.append(room)
        self.window.repaint()
