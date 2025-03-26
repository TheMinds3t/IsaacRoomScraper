import PyQt6.QtGui
import PyQt6.Qt6
import structs 
import stage_parser 
import config
import math

# import PyQt6.QtWidgets as qt
from PyQt6.QtWidgets import QVBoxLayout, QApplication, QLabel, QWidget, QPushButton, QScrollArea, QGridLayout, QVBoxLayout,  QLayout, QSizePolicy, QListWidget, QListWidgetItem, QTextEdit, QCheckBox
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QResizeEvent, QMoveEvent, QFont
from PyQt6.QtCore import QMargins, QPoint, QRect, QSize, Qt, QModelIndex, pyqtSlot, QRunnable

class QWorker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, funct, *args, **kwargs):
        super().__init__()
        self.funct = funct
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.funct(*self.args, **self.kwargs)



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


class QCheckPanel(QScrollArea):
    def __init__(self, gui, parent:QWidget = None):
        super().__init__(parent=parent)
        self.setWidgetResizable(True)
        self.setMinimumSize(256, 64)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.panel = QWidget()

        self.check_layout = QVBoxLayout()
        self.check_layout.setSpacing(0)
        self.check_layout.setContentsMargins(5,5,5,5)
        self.panel.setLayout(self.check_layout)

        self.setWidget(self.panel)
        self.checks = dict[str,QCheckBox]()
        self.gui = gui 

    def add_checkbox(self, text:str):
        if text != None and text not in self.checks.keys():
            self.checks[text] = QCheckBox(text,self)
            self.checks[text].setChecked(True)
            self.checks[text].setMaximumHeight(self.checks[text].font().pointSize()*2)
            self.checks[text].checkStateChanged.connect(slot=self.checkbox_change)
            self.check_layout.addWidget(self.checks[text])

    def checkbox_change(self, checkbox:Qt.CheckState):
        pass

    def get_checkbox_states(self) -> dict[str,int]:
        ret = {}

        for key in self.checks.keys():
            ret[key] = self.checks[key].checkState().value

        return ret 
    
    def remove_checkbox(self, text:str):
        if text in self.checks.keys():
            self.check_layout.removeWidget(self.checks[text])
            self.checks[text].setParent(None)
            self.checks.pop(text)

    def set_checkbox(self, text:str, state:Qt.CheckState):
        if text in self.checks.keys():
            self.checks[text].setCheckState(state)

    def clear_checkboxes(self):
        cache = []
        for key in self.checks.keys():
            self.checks[key].setParent(None)
        
        self.checks.clear()

class QCheckPanelLabel(QWidget):
    def __init__(self, panel: QCheckPanel = None, title: str = None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.layout = QGridLayout(parent=self)
        self.setLayout(self.layout)
        self.panel = panel 

        self.check_all_but = QPushButton(text="Check All",parent=self)
        self.check_all_but.clicked.connect(self.check_all)
        self.uncheck_all_but = QPushButton(text="Uncheck All",parent=self)
        self.uncheck_all_but.clicked.connect(self.uncheck_all)

        self.title = QLabel(text=title,parent=self)
        font = QFont(self.title.font())
        font.setPointSize(14)
        self.title.setFont(font)

        self.layout.addWidget(self.title,1,1,1,2)
        self.layout.addWidget(self.check_all_but,2,1,1,1)
        self.layout.addWidget(self.uncheck_all_but,2,2,1,1)

    def check_all(self):
        for item in self.panel.checks.keys():
            self.panel.set_checkbox(item, Qt.CheckState.Checked)
    
    def uncheck_all(self):
        for item in self.panel.checks.keys():
            self.panel.set_checkbox(item, Qt.CheckState.Unchecked)

class QEntityTile(QWidget):
    def __init__(self, entry: structs.Entry, group_panel:QCheckPanel = None, kind_panel:QCheckPanel = None, parent: QWidget = None):
        super().__init__(parent=parent)
        self.entry = entry 
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMaximumSize(128,160)
        self.id_label = QLabel(self.entry.type_string())
        
        self.setFixedSize(128,96)
        self.br_entry = stage_parser.get_br_entry(self.entry)

        if self.br_entry:
            self.img = QImage(self.br_entry.image)
            self.img_label = QLabel(parent=self)
            self.img_label.setPixmap(QPixmap(self.img))
            self.layout.addWidget(self.img_label)
            self.id_label.setText(f"{self.br_entry.name}\n{self.entry.type_string()}\n{self.br_entry.group},{self.br_entry.kind}")
            
            if self.br_entry.group != None:
                group_panel.add_checkbox(f"Group: {self.br_entry.group}")
            
            if self.br_entry.kind != None:
                kind_panel.add_checkbox(f"Kind: {self.br_entry.kind}")

            id_size = self.id_label.fontMetrics().boundingRect(self.id_label.text())
            self.setFixedSize(max(self.img.width()*2,math.floor(id_size.width()*1.25)),self.img.height()+id_size.height()*2+64)

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

class MainGUI:
    
    def prompt_for_room(self, event = None, file: str = None):
        roomlist, filename = stage_parser.parse_stage(file)

        if filename != None:
            for room in roomlist:
                self.add_room(room)
            self.loaded_file_list.addItem(QListWidgetItem(filename, self.loaded_file_list))
            self.window.repaint()

    def __init__(self, rooms: list):
        self.app = QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle("Isaac Room Statistics by MINDS3T")
        self.window.setGeometry(config.settings["XPos"], config.settings["YPos"], config.settings["Width"], config.settings["Height"])
        self.window.resizeEvent = lambda e: self.resized(e)
        self.window.moveEvent = lambda e: self.moved(e)

        self.layout = QGridLayout(parent=self.window)
        self.window.setLayout(self.layout)

        self.ent_tile_scroll_area = QScrollArea()
        self.ent_tile_layout = QFlowLayout()
        self.ent_tile_layout.setSpacing(32)
        self.ent_tile_layout.setContentsMargins(5,5,5,5)

        self.ent_tile_area = QWidget()
        self.ent_tile_area.setLayout(self.ent_tile_layout)
        self.ent_tile_scroll_area.setWidgetResizable(True)
        self.ent_tile_scroll_area.setMinimumSize(256, 128)
        self.ent_tile_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.ent_tile_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ent_tile_scroll_area.setWidget(self.ent_tile_area)

        # room file list 
        self.loaded_file_list = QListWidget(parent=self.window)
        self.loaded_file_list.setSortingEnabled(True)
        self.loaded_file_list.keyPressEvent = lambda e: self.list_keypress(e)
        self.list_title = QLabel(parent=self.window)
        self.list_title.setText("Loaded Files:")
        self.list_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        self.list_title.setMaximumHeight(24)
        font = QFont(self.list_title.font())
        font.setPointSize(14)
        self.list_title.setFont(font)

        # add room / add basement renovator file 
        self.add_room_button = QPushButton(text="Add Stage Roomlist XML",parent=self.window)
        self.add_room_button.clicked.connect(self.prompt_for_room)
        self.add_br_button = QPushButton(text="Add Basement Renovator Entity XMLs For Images",parent=self.window)
        self.add_br_button.clicked.connect(self.prompt_for_br)
        self.cur_entity_tiles = dict[str,QEntityTile]()
        self.loaded_rooms = list()

        self.search_bar = QTextEdit(parent=self.window)
        self.search_bar.textChanged.connect(self.search_keypress)
        self.search_bar.setPlaceholderText("Search entity list...")

        # searchKey = self.search_bar.keyPressEvent
        # self.search_bar.keyPressEvent = lambda e: self.search_keypress(searchKey, e)
        self.group_filter = QCheckPanel(self, parent=self.window)
        self.group_filter.checkbox_change = self.checkbox_change
        self.kind_filter = QCheckPanel(self, parent=self.window)
        self.kind_filter.checkbox_change = self.checkbox_change

        self.group_filter_title = QCheckPanelLabel(parent=self.window,panel=self.group_filter,title="Available Groups:")
        # self.group_filter_title.setMaximumHeight(48)

        self.kind_filter_title = QCheckPanelLabel(parent=self.window,panel=self.kind_filter,title="Available Kinds:")
        # self.kind_filter_title.setMaximumHeight(48)

        self.layout.setColumnMinimumWidth(1,128)
        # self.layout.setColumnMinimumWidth(3,96)
        # self.layout.setRowMinimumHeight(3,10)
        # self.layout.setRowMinimumHeight(6,10)
        # self.layout.setRowMinimumHeight(2,24)
        # self.layout.setRowMinimumHeight(3,24)
        # self.layout.setRowMinimumHeight(4,48)
        self.layout.addWidget(self.add_room_button,1,1,1,1)
        self.layout.addWidget(self.add_br_button,2,1,1,1)
        self.layout.addWidget(self.list_title,3,1,1,2,QtCore.Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.loaded_file_list,4,1,2,2)
        self.layout.addWidget(self.group_filter_title,6,1,1,2,QtCore.Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.group_filter, 7, 1, 2, 2)
        self.layout.addWidget(self.kind_filter_title,9,1,1,2,QtCore.Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.kind_filter, 10, 1, 2, 2)

        self.layout.addWidget(self.ent_tile_scroll_area,3,3,9,2)
        self.layout.addWidget(self.search_bar, 1, 3, 2, 1)


        for file in rooms:
            self.prompt_for_room(file=file)

        self.window.show()
        self.group_checkbox_cache = self.group_filter.get_checkbox_states()
        self.kind_checkbox_cache = self.kind_filter.get_checkbox_states()

    def resized(self, e: QResizeEvent):
        config.settings["Width"] = e.size().width()
        config.settings["Height"] = e.size().height()

    def moved(self, e: QMoveEvent):
        config.settings["XPos"] = e.pos().x()
        config.settings["YPos"] = e.pos().y()

    def prompt_for_br(self):
        stage_parser.scrape_br_file()
        self.window.repaint()

    def checkbox_change(self, checkbox:Qt.CheckState):
        self.group_checkbox_cache = self.group_filter.get_checkbox_states()
        self.kind_checkbox_cache = self.kind_filter.get_checkbox_states()
        self.window.repaint()
        self.apply_entity_filters()

    def apply_entity_filters(self):
        for entkey in self.cur_entity_tiles.keys():
            tile = self.cur_entity_tiles[entkey]

            if self.should_filter(tile):
                tile.setHidden(True)
                self.ent_tile_layout.removeWidget(tile)
            else:
                tile.setHidden(False)
                self.ent_tile_layout.addWidget(tile)

    def should_filter(self, tile:QEntityTile):
        text = self.search_bar.toPlainText().lower()

        if tile.br_entry:
            groupkey = f"Group: {tile.br_entry.group}"
            kindkey = f"Kind: {tile.br_entry.kind}"
            if groupkey in self.group_checkbox_cache.keys() and self.group_checkbox_cache[groupkey] == 0:
                return True 
            if kindkey in self.kind_checkbox_cache.keys() and self.kind_checkbox_cache[kindkey] == 0:
                return True 
            
        return (tile.id_label.text().lower().find(text) == -1 and len(text) != 0)

    def search_keypress(self):
        self.apply_entity_filters()

    def list_keypress(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Delete:
            self.remove_roomlist(self.loaded_file_list.currentItem())

    def remove_roomlist(self, sel_file:QListWidgetItem):
        print(f"Unloaded \'{sel_file.text()}\'")
        self.loaded_file_list.update()
        self.loaded_file_list.repaint()
        config.settings["RoomFiles"].remove(self.loaded_file_list.takeItem(self.loaded_file_list.currentIndex().row()).text())
        
        self.update_entity_tiles()

    def add_room(self, room: structs.Room):
        for spawn in room.spawns:
            new_tile = QEntityTile(parent=self.ent_tile_area,entry=spawn.entry,group_panel=self.group_filter,kind_panel=self.kind_filter)

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

    def update_entity_tiles(self):
        for key in self.cur_entity_tiles.keys():
            tile = self.cur_entity_tiles[key]
            self.ent_tile_layout.removeWidget(tile)
            tile.setParent(None)

        self.cur_entity_tiles.clear()
        loaded_files = self.loaded_file_list.count()
        self.group_filter.clear_checkboxes()
        self.kind_filter.clear_checkboxes()

        for ind in range(0,loaded_files):
            file = self.loaded_file_list.item(ind)
            if isinstance(file, QListWidgetItem):
                print(f"Reloading \'{file.text()}\'..")
                stage,filename = stage_parser.parse_stage(file.text())

                if stage != None:
                    for room in stage:
                        self.add_room(room)

        self.window.repaint()
