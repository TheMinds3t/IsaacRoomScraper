import PyQt6.QtGui
import PyQt6.Qt6
import structs 
import stage_parser 
import config
import math

# import PyQt6.QtWidgets as qt
from PyQt6.QtWidgets import QVBoxLayout, QApplication, QLabel, QWidget, QPushButton, QScrollArea, QGridLayout, QVBoxLayout,  QLayout, QSizePolicy, QListWidget, QListWidgetItem
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QResizeEvent, QMoveEvent
from PyQt6.QtCore import QMargins, QPoint, QRect, QSize, Qt

class QEntityTile(QWidget):
    def __init__(self, entry: structs.Entry, parent: QWidget):
        super().__init__(parent=parent)
        self.entry = entry 
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMaximumSize(128,160)
        self.id_label = QLabel(self.entry.type_string())
        self.setFixedSize(128,96)

        ent_info = stage_parser.get_br_entry(self.entry)
        if ent_info:
            self.img = QImage(ent_info.image)
            self.img_label = QLabel(parent=self)
            self.img_label.setPixmap(QPixmap(self.img))
            self.setFixedSize(max(math.floor(self.img.width()*2),128),max(math.floor(self.img.height()*1.5)+64,96))
            self.layout.addWidget(self.img_label)
            self.id_label.setText(f"{ent_info.name}\n{self.entry.type_string()}")

        self.layout.addWidget(self.id_label)
        self.quantity_label = QLabel("Quantity: 1",parent=self)
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

# sourced from https://doc.qt.io/qtforpython-6/examples/example_widgets_layouts_flowlayout.html
class QFlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item: QWidget):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(QFlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def update(self):
        super(QFlowLayout, self).update()
        self._do_layout(self.geometry(), False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.sizeHint())

        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()
    
    def paintEvent(self, e):
        super().paintEvent(e)
        for item in self._item_list:
            item.paintEvent(e)


class MainGUI:
    def resized(self, e: QResizeEvent):
        config.settings["Width"] = e.size().width()
        config.settings["Height"] = e.size().height()

    def moved(self, e: QMoveEvent):
        config.settings["XPos"] = e.pos().x()
        config.settings["YPos"] = e.pos().y()

    def __init__(self, rooms: list):
        self.app = QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle("Isaac Room Statistics by MINDS3T")
        self.window.setGeometry(config.settings["XPos"], config.settings["YPos"], config.settings["Width"], config.settings["Height"])
        self.window.resizeEvent = lambda e: self.resized(e)
        self.window.moveEvent = lambda e: self.moved(e)

        self.layout = QGridLayout(parent=self.window)
        self.layout.setColumnMinimumWidth(1,96)
        self.layout.setColumnMinimumWidth(3,96)
        self.layout.setRowMinimumHeight(1,24)
        self.layout.setRowMinimumHeight(2,24)
        self.layout.setRowMinimumHeight(3,48)
        self.window.setLayout(self.layout)

        self.ent_tile_scroll_area = QScrollArea()
        self.ent_tile_layout = QFlowLayout()
        self.ent_tile_layout.setSpacing(32)
        self.ent_tile_layout.setContentsMargins(5,5,5,5)

        self.ent_tile_area = QWidget()
        self.ent_tile_area.setLayout(self.ent_tile_layout)
        self.ent_tile_scroll_area.setWidgetResizable(True)
        self.ent_tile_scroll_area.setMinimumSize(256, 128)
        self.ent_tile_scroll_area.setMaximumSize(1024,1024)
        self.ent_tile_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.ent_tile_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ent_tile_scroll_area.setWidget(self.ent_tile_area)
        
        self.layout.addWidget(self.ent_tile_scroll_area,1,3,5,2)

        # room file list 
        self.loaded_file_list = QListWidget(parent=self.window)
        self.loaded_file_list.setSortingEnabled(True)
        self.list_title = QLabel(parent=self.window)
        self.list_title.setText("Loaded Files:")
        self.layout.addWidget(self.list_title,3,1,1,2)
        self.layout.addWidget(self.loaded_file_list,4,1,2,2)

        # add room / add basement renovator file 
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
        self.update_loaded_file_list()
        self.window.repaint()

    def prompt_for_br(self):
        stage_parser.scrape_br_file()
        self.window.repaint()


    def list_keypress(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Delete:
            self.remove_roomlist(self.loaded_file_list.selectedItems())

    def update_loaded_file_list(self):
        self.loaded_file_list.clear()
        self.loaded_file_list.keyPressEvent = lambda e: self.list_keypress(e)

        for file in stage_parser.loaded_files:
            item = QListWidgetItem(file, self.loaded_file_list)
            self.loaded_file_list.addItem(item)

        self.loaded_file_list.update()
    
    def remove_roomlist(self, file_list:list):
        for file in file_list:
            stage_parser.unload_file(file.text())
            print(f"Unloaded \'{file.text()}\'")
        
        self.update_loaded_file_list()
        self.updateEntityTiles()

    def add_room(self, room: structs.Room):
        for spawn in room.spawns:
            new_tile = QEntityTile(parent=self.ent_tile_area,entry=spawn.entry)

            if spawn.entry.type_string() in self.cur_entity_tiles.keys():
                self.cur_entity_tiles[spawn.entry.type_string()].increment_quantity()
            else:
                x_ind = math.ceil((len(self.cur_entity_tiles)+1) / 4) - 1
                y_ind = len(self.cur_entity_tiles) % 4
                self.ent_tile_layout.addWidget(new_tile)
                # self.ent_tile_layout.update()
                self.cur_entity_tiles[spawn.entry.type_string()] = new_tile
    
        self.loaded_rooms.append(room)
        self.window.repaint()

    def updateEntityTiles(self):
        for key in self.cur_entity_tiles.keys():
            tile = self.cur_entity_tiles[key]
            self.ent_tile_layout.removeWidget(tile)
            tile.setParent(None)

        self.cur_entity_tiles.clear()

        for file in stage_parser.loaded_files:
            for room in stage_parser.parse_stage(file):
                self.add_room(room)


        self.window.repaint()
