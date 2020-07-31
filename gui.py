import csv
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import config
from Message import Message


class MyQComboBox(QComboBox):
    def __init__(self, row, column):
        self.row = row
        self.column = column
        super().__init__()


class ErrorMessage(Message):
    def __init__(self):
        self.hide = False
        self.comboBox = False
        self.description = ""

    def is_value_allowed(self, value):
        return "Spalte zu viel"


class UiMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # contains no_error bool [0]
        # users (values) [1-x]
        # if error users [value, error]
        self.users = []
        self.headers = []
        self.headersHidden = []
        self.countLines = 0

        self.pages = 0
        self.currentPage = 0
        self.currentFile = ""
        self.hideCols = False
        self.allowComboBox = True

        self.onCheck = False

        self.config = config.Config()
        self.config.read_Config()
        self.read_Sections = self.config.read_Sections.copy()
        self.lines_Site = self.config.linesperpage

        # Setup Ui
        self.setObjectName("MainWindow")
        self.resize(1200, 1000)
        self.setWindowIcon(QIcon("./logo.png"))
        self.setWindowTitle("CSV_VaTa")
        self.setAcceptDrops(False)

        # Init menubar
        menubar = self.menuBar()
        file = menubar.addMenu("File")
        new_file = QAction("New File from config", self)
        new_file.setShortcut('Ctrl+N')
        new_file.triggered.connect(self.newPageFromConfig)
        file.addAction(new_file)

        open = QAction("Open File", self)
        open.setShortcut('Ctrl+O')
        open.triggered.connect(self.chooseFile)
        file.addAction(open)

        save = QAction("&Save File", self)
        save.setShortcut('Ctrl+S')
        save.triggered.connect(self.file_save_current)
        file.addAction(save)

        save_as = QAction("&Save as File", self)
        save_as.setShortcut('Ctrl+Shift+S')
        save_as.triggered.connect(self.file_save_as)
        file.addAction(save_as)

        edit = menubar.addMenu("Edit")
        add = QAction("&New line", self)
        add.setShortcut('Insert')
        add.triggered.connect(self.addNewLine)
        edit.addAction(add)

        dell_line = QAction("&Delete Line", self)
        dell_line.setShortcut('Delete')
        dell_line.triggered.connect(self.delline)
        edit.addAction(dell_line)
        hide_columns = QAction("Hide unused colums", self)
        hide_columns.setShortcut('Ctrl+H')
        hide_columns.triggered.connect(self.hideUnusedColums)
        edit.addAction(hide_columns)

        allow_combo_box = QAction("Disable ComboBoxes", self)
        allow_combo_box.triggered.connect(self.allow_comboBox)
        edit.addAction(allow_combo_box)

        help = menubar.addMenu("Help")

        # Init tableWiget
        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)

        # Init pages-windows (DockWidget)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_back = QPushButton("zurück  (Ctrl+Left)")
        self.pushButton_back.setObjectName("pushButton_back")
        self.pushButton_back.setShortcut("Ctrl+Left")
        self.pushButton_back.clicked.connect(self.backPage)
        self.horizontalLayout.addWidget(self.pushButton_back)
        self.lcd_current_Page = QLCDNumber()
        self.lcd_current_Page.setSmallDecimalPoint(False)
        self.lcd_current_Page.setObjectName("lcdNumber")
        self.horizontalLayout.addWidget(self.lcd_current_Page)
        self.label = QLabel("/")
        self.label.setEnabled(False)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lcd_max_Page = QLCDNumber()
        self.lcd_max_Page.setObjectName("lcdNumber_max")
        self.horizontalLayout.addWidget(self.lcd_max_Page)
        self.pushButton_vor = QPushButton("vor  (Ctrl+Right)")
        self.pushButton_vor.setObjectName("pushButton_vor")
        self.pushButton_vor.setShortcut("Ctrl+Right")
        self.pushButton_vor.clicked.connect(self.vorPage)
        self.horizontalLayout.addWidget(self.pushButton_vor)

        column = QOpenGLWidget()

        column.setLayout(self.horizontalLayout)
        doc_bottom = QDockWidget("Bottom", self)
        doc_bottom.setAllowedAreas(Qt.BottomDockWidgetArea)
        doc_bottom.setWidget(column)
        doc_bottom.setFixedHeight(75)
        self.addDockWidget(Qt.BottomDockWidgetArea, doc_bottom)

        # show Window
        self.show()

        # try read last file
        file = self.config.lastFile
        if os.path.isfile(file):
            if self.csv_load(file):
                self.calcPages()
                self.setCurrentPage(0, self.lines_Site)
        else:
            self.currentFile = ""
            self.config.save_currentFile("")
            self.newPageFromConfig()

    def allow_comboBox(self):
        if self.file_loaded():
            sender = self.sender()
            self.allowComboBox = not self.allowComboBox
            if self.allowComboBox:
                sender.setText("Hide ComboBoxes")
            else:
                sender.setText("Show ComboBoxes")
            self.setCurrentPage(self.currentPage * self.lines_Site, (self.currentPage + 1) * self.lines_Site)

    def hideUnusedColums(self):
        if self.file_loaded():
            sender = self.sender()

            self.hideCols = not self.hideCols
            if self.hideCols:
                sender.setText("Unhide unused colums")
            else:
                sender.setText("Hide unused colums")
            self.setCurrentPage(self.currentPage * self.lines_Site, (self.currentPage + 1) * self.lines_Site)

    def addNewLine(self):
        if self.file_loaded():
            user = [0]
            for section in self.read_Sections:
                checked = section.is_value_allowed(section.default_values)
                if checked == "Ok":
                    user.append(section.default_values)
                else:
                    user.append([section.default_values, checked])
                    user[0] += 1

            self.users.append(user)
            self.countLines = len(self.users) - 1
            self.calcPages()
            self.currentPage = self.pages - 1
            self.lcd_current_Page.display(str(self.currentPage + 1))
            self.setCurrentPage((self.pages - 1) * self.lines_Site, self.pages * self.lines_Site)

    def vorPage(self):
        if self.file_loaded():
            if self.currentPage < self.pages - 1:
                self.setCurrentPage((self.currentPage + 1) * self.lines_Site, (self.currentPage + 2) * self.lines_Site)
                self.currentPage += 1
                self.lcd_current_Page.display(str(self.currentPage + 1))

    def backPage(self):
        if self.file_loaded():
            if self.currentPage > 0:
                self.setCurrentPage((self.currentPage - 1) * self.lines_Site, self.currentPage * self.lines_Site)
                self.currentPage -= 1
                self.lcd_current_Page.display(str(self.currentPage + 1))

    def initPage(self, file):
        if self.csv_load(file):
            self.calcPages()
            self.setCurrentPage(0, self.lines_Site)

    def newPageFromConfig(self):
        ok = False
        self.read_Sections = self.config.read_Sections.copy()
        if self.currentFile != "":
            msg = QMessageBox()
            msg.addButton("Ja", QMessageBox.YesRole)
            msg.addButton("Nein", QMessageBox.NoRole)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warnung")
            msg.setText("Achtung")
            msg.setInformativeText(
                "Das erstellen einer neuen Datei verwirft alle Änderungen.\nMöchten Sie dennoch laden?")
            if not msg.exec_():
                ok = True
        else:
            ok = True
        if ok:
            self.headers = []
            self.headersHidden = []
            for section in self.read_Sections:
                self.headers.append(section.name)
                if not section.hide:
                    self.headersHidden.append(section.name)
            self.users = []
            self.countLines = len(self.users) - 1
            self.calcPages()
            self.setCurrentPage(0, 0)
            self.currentFile = " "

    def calcPages(self):
        self.pages = int(self.countLines / self.lines_Site) + 1
        if self.lines_Site > 0:
            self.lcd_current_Page.display("1")
            self.lcd_max_Page.display(str(self.pages))

    def setCurrentPage(self, fr, to):
        self.tableWidget = QTableWidget()

        self.setCentralWidget(self.tableWidget)
        if self.hideCols:
            self.tableWidget.setColumnCount(len(self.headersHidden))

        else:
            self.tableWidget.setColumnCount(len(self.headers))

        if to > self.countLines:
            self.tableWidget.setRowCount(1 + self.countLines - fr)

        else:
            self.tableWidget.setRowCount(self.lines_Site)
        vertikal_header = []

        for row, allowed_value in enumerate(range(fr, to)):
            if allowed_value < len(self.users):
                user = self.users[allowed_value]
                skipped = 0
                if user[0] == 0:
                    for i, (value_user, section) in enumerate(zip(user[1:], self.read_Sections)):
                        if section.hide and self.hideCols:
                            skipped += 1
                        else:
                            if self.allowComboBox and section.comboBox:
                                index = -1
                                combo_box = MyQComboBox(row, i - skipped)
                                combo_box.setStyleSheet("QComboBox"
                                                       "{"
                                                       "background-color : white;"
                                                       "}")
                                combo_box.setToolTip("Description: " + section.description)

                                for x, allowed in enumerate(section.allowed_values):
                                    combo_box.addItem(allowed)
                                    if allowed == value_user:
                                        index = x

                                combo_box.setEditable(False)
                                if index == -1:
                                    index = combo_box.count()
                                    model = combo_box.model()
                                    item = QStandardItem()
                                    item.setText(value_user)
                                    item.setBackground(QColor(255, 0, 0))
                                    model.appendRow(item)
                                combo_box.setCurrentIndex(index)
                                combo_box.currentIndexChanged.connect(self.save_ComboBox)
                                self.tableWidget.setCellWidget(row, i - skipped, combo_box)
                            else:
                                self.tableWidget.setItem(row, i - skipped, QTableWidgetItem(value_user))
                                self.tableWidget.item(row, i - skipped).setToolTip(
                                    "Description: " + section.description)
                else:
                    for i, (value_user, section) in enumerate(zip(user[1:], self.read_Sections)):
                        if section.hide and self.hideCols:
                            skipped += 1
                        else:
                            error: bool = False
                            if isinstance(value_user, list):
                                error = True
                                value = value_user[0]
                            else:
                                value = value_user
                            if self.allowComboBox and section.comboBox:
                                index = -1
                                combo_box = MyQComboBox(row, i - skipped)
                                for x, allowed in enumerate(section.allowed_values):
                                    combo_box.addItem(allowed)
                                    if allowed == value:
                                        index = x

                                combo_box.setEditable(False)
                                if index == -1:
                                    index = combo_box.count()
                                    model = combo_box.model()
                                    item = QStandardItem()
                                    item.setText(value)

                                    item.setBackground(QColor(255, 0, 0))
                                    model.appendRow(item)
                                combo_box.setCurrentIndex(index)
                                if not error:
                                    combo_box.setStyleSheet("QComboBox"
                                                           "{"
                                                           "background-color : gray;"
                                                           "}")
                                    combo_box.setToolTip("Description: " + section.description)

                                else:
                                    combo_box.setStyleSheet("QComboBox"
                                                           "{"
                                                           "background-color : red;"
                                                           "}")
                                    combo_box.setToolTip("Description: " + section.description + "\n" + value_user[1])
                                    combo_box.currentIndexChanged.connect(self.save_ComboBox)
                                self.tableWidget.setCellWidget(row, i - skipped, combo_box)
                            else:
                                self.tableWidget.setItem(row, i - skipped, QTableWidgetItem(value))
                                if error:
                                    self.tableWidget.item(row, i - skipped).setBackground(QColor(255, 0, 0))
                                    self.tableWidget.item(row, i - skipped).setToolTip(
                                        "Description: " + section.description + "\n" + value_user[1])

                                else:
                                    self.tableWidget.item(row, i - skipped).setBackground(QColor(140, 140, 140))
                                    self.tableWidget.item(row, i - skipped).setToolTip(
                                        "Description: " + section.description)

            vertikal_header.append(str(allowed_value))
        if self.hideCols:
            self.tableWidget.setHorizontalHeaderLabels(self.headersHidden)
        else:
            self.tableWidget.setHorizontalHeaderLabels(self.headers)
        self.tableWidget.setVerticalHeaderLabels(vertikal_header)
        self.tableWidget.itemChanged.connect(self.save_item)

    def save_item(self, item):
        if not self.onCheck:
            self.onCheck = True
            if self.hideCols:
                count = 0
                for column, section in enumerate(self.read_Sections):
                    if count == item.column():
                        current_column = column
                        break
                    if not section.hide:
                        count += 1
            else:
                current_column = item.column()
            testing = self.read_Sections[item.column()].is_value_allowed(item.text())
            if testing != "Ok":
                self.tableWidget.item(item.row(), item.column()).setBackground(QColor(255, 0, 0))
                self.tableWidget.item(item.row(), item.column()).setToolTip(
                    "Description: " + self.read_Sections[current_column].description + "\n" + testing)
                if (
                not isinstance(self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1],
                               list)):
                    self.users[self.currentPage * self.config.linesperpage + item.row()][0] += 1
                    if self.users[self.currentPage * self.config.linesperpage + item.row()][0] == 1:
                        skipped = 0
                        for column in range(
                                len(self.users[self.currentPage * self.config.linesperpage + item.row()]) - 1):
                            if self.read_Sections[column].hide and self.hideCols:
                                skipped += 1
                            else:
                                if column - skipped != current_column:
                                    if self.allowComboBox and self.read_Sections[column].comboBox:
                                        combo_box = self.tableWidget.cellWidget(item.row(), column - skipped)
                                        combo_box.setStyleSheet("QComboBox"
                                                               "{"
                                                               "background-color : gray;"
                                                               "}")

                                    else:
                                        self.tableWidget.item(item.row(), column - skipped).setBackground(
                                            QColor(140, 140, 140))
                self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1] = [item.text(),
                                                                                                            testing]
            else:
                if (isinstance(self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1],
                               list)):
                    self.users[self.currentPage * self.config.linesperpage + item.row()][0] -= 1
                    self.tableWidget.item(item.row(), item.column()).setToolTip(
                        "Description: " + self.read_Sections[current_column].description)
                    if self.users[self.currentPage * self.config.linesperpage + item.row()][0] == 0:
                        skipped = 0
                        for column, section in enumerate(self.read_Sections):
                            if section.hide and self.hideCols:
                                skipped += 1
                            else:
                                if self.allowComboBox and section.comboBox:
                                    combo_box = self.tableWidget.cellWidget(item.row(), column - skipped)
                                    combo_box.setStyleSheet("QComboBox"
                                                           "{"
                                                           "background-color : white;"
                                                           "}")

                                else:
                                    self.tableWidget.item(item.row(), column - skipped).setBackground(
                                        QColor(255, 255, 255))
                    else:
                        self.tableWidget.item(item.row(), current_column).setBackground(QColor(140, 140, 140))
                self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1] = item.text()
            self.onCheck = False

    def save_ComboBox(self):
        if not self.onCheck:
            self.onCheck = True
            combo_box = self.sender()

            if self.hideCols:
                count = 0
                for column, section in enumerate(self.read_Sections):
                    if count == combo_box.column:
                        current_column = column
                        break
                    if not section.hide:
                        count += 1
            else:
                current_column = combo_box.column
            if combo_box.currentIndex() + 1 <= len(self.read_Sections[current_column].allowed_values):
                if (
                isinstance(self.users[self.currentPage * self.config.linesperpage + combo_box.row][current_column + 1],
                           list)):
                    self.users[self.currentPage * self.config.linesperpage + combo_box.row][0] -= 1

                    combo_box.setToolTip("Description: " + self.read_Sections[current_column].description)
                    if self.users[self.currentPage * self.config.linesperpage + combo_box.row][0] == 0:
                        skipped = 0
                        for column, section in enumerate(self.read_Sections):
                            if section.hide and self.hideCols:
                                skipped += 1
                            else:
                                if self.allowComboBox and section.comboBox:
                                    combo_box_temp = self.tableWidget.cellWidget(combo_box.row, column - skipped)
                                    combo_box_temp.setStyleSheet("QComboBox"
                                                                "{"
                                                                "background-color : white;"
                                                                "}")

                                else:
                                    self.tableWidget.item(combo_box.row, column - skipped).setBackground(
                                        QColor(255, 255, 255))
                    else:
                        combo_box.setStyleSheet("QComboBox"
                                               "{"
                                               "background-color : gray;"
                                               "}")

                self.users[self.currentPage * self.config.linesperpage + combo_box.row][
                    current_column + 1] = combo_box.currentText()

            else:
                if (not isinstance(
                        self.users[self.currentPage * self.config.linesperpage + combo_box.row][current_column + 1],
                        list)):
                    combo_box.setStyleSheet("QComboBox"
                                           "{"
                                           "background-color : red;"
                                           "}")
                    combo_box.setToolTip(
                        "Description: " + self.read_Sections[current_column].description + "\nUnerlaubter Wert.")
                    self.users[self.currentPage * self.config.linesperpage + combo_box.row][0] += 1
                    if self.users[self.currentPage * self.config.linesperpage + combo_box.row][0] == 1:
                        skipped = 0
                        for column, section in enumerate(self.read_Sections):
                            if section.hide and self.hideCols:
                                skipped += 1
                            else:
                                if column - skipped != current_column:
                                    if self.allowComboBox and section.comboBox:
                                        combo_box_temp = self.tableWidget.cellWidget(combo_box.row, column - skipped)
                                        combo_box_temp.setStyleSheet("QComboBox"
                                                                    "{"
                                                                    "background-color : gray;"
                                                                    "}")

                                    else:
                                        self.tableWidget.item(combo_box.row, column - skipped).setBackground(
                                            QColor(140, 140, 140))
                self.users[self.currentPage * self.config.linesperpage + combo_box.row][current_column + 1] = \
                    [combo_box.currentText(), "Uneralaubter Wert."]
        self.onCheck = False

    def delline(self):
        if self.file_loaded():
            if self.tableWidget.rowCount() > 0:
                i, ok_pressed = QInputDialog.getInt(self, "Get integer", "Line number:", self.tableWidget.currentRow(),
                                                   0, self.countLines, 1)
                if ok_pressed:
                    self.users.pop(i)
                    if self.countLines == 0:
                        self.currentPage = 0
                        self.lcd_current_Page.display("0")
                        self.lcd_max_Page.display("0")
                        self.tableWidget.removeRow(0)
                    else:
                        self.countLines = len(self.users) - 1
                        self.calcPages()
                        self.setCurrentPage(self.currentPage * self.lines_Site,
                                            (self.currentPage + 1) * self.lines_Site)

    def file_save_current(self):
        if self.file_loaded():
            if os.path.isfile(self.currentFile):
                self.file_save(self.currentFile)
            else:
                self.file_save_as()

    def file_save(self, file):
        if file != "":
            self.saveCSV(file)

    def file_save_as(self):
        if self.file_loaded():
            filename = QFileDialog.getSaveFileName(
                self, self.tr('Import file'), '',
                '(*.csv);;' + self.tr('All files(*)'))
            if filename != ('', ''):
                self.file_save(filename[0])

    def saveCSV(self, file) -> bool:
        with open(file, 'w', newline='', encoding=self.config.encoding) as file:
            writer = csv.writer(file, delimiter=';', quotechar='"')
            writer.writerow(self.headers)
            continue_anyway = False

            for row in self.users:
                for x2, (value, header) in enumerate(zip(row[1:], self.headers)):
                    if row[0] > 0:
                        if isinstance(value, list) and not continue_anyway:
                            msg = QMessageBox()
                            msg.addButton("Ja", QMessageBox.YesRole)
                            msg.addButton("Nein", QMessageBox.NoRole)
                            msg.setIcon(QMessageBox.Warning)
                            msg.setWindowTitle("Warnung")
                            msg.setText("Die Daten sind fehlerhaft\n Möchten Sie dennoch speichern?")
                            msg.setInformativeText(
                                'Der Datensatz in Zeile"' + str(
                                    x2) + '" in Spalte: "' + header + '" ist Fehlerhaft.\n' + value[1])
                            cb = QCheckBox("Alle ignorieren")
                            msg.setCheckBox(cb)
                            if msg.exec_():
                                print("Cancel")
                                return False
                            else:
                                continue_anyway = msg.checkBox().isChecked()

            for row in self.users:
                out = []
                for value in row[1:]:
                    if isinstance(value, list):
                        out.append(value[0])
                    else:
                        out.append(value)
                print(out)
                writer.writerow(out)
            return True

    def chooseFile(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr('Import file'), '',
            '(*.csv);;' + self.tr('All files(*)'))
        if filename != ('', ''):
            self.initPage(filename[0])

    def csv_load(self, file) -> bool:
        old_read_sections = self.read_Sections.copy()
        self.read_Sections = self.config.read_Sections.copy()
        old_file = self.currentFile
        self.currentFile = file
        temp_users = self.users.copy()
        temp_headers = self.headers.copy()
        temp_headers_hidden = self.headersHidden.copy()
        self.headers = []
        self.users = []
        encoding_temp = self.config.encoding
        try:
            with open(file, newline='', encoding=encoding_temp) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
                fields = reader.fieldnames

                print(fields)
                continue_anyway = False
                if len(self.read_Sections) == len(fields):
                    for x in range(len(fields)):
                        if self.read_Sections[x].name != fields[x] and not continue_anyway:
                            print("warnung nicht gleich")
                            msg = QMessageBox()
                            msg.addButton("Ja", QMessageBox.YesRole)
                            msg.addButton("Nein", QMessageBox.NoRole)
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Die Header stimmen nicht überein")
                            msg.setInformativeText('Der Header "' + fields[x] + '" sollte "' + self.read_Sections[
                                x].name + '" sein. \n Möchten Sie dennoch laden?')
                            msg.setWindowTitle("Warning")
                            cb = QCheckBox("Alle ignorieren")
                            msg.setCheckBox(cb)
                            if msg.exec_():
                                print("Cancel")
                                self.users = temp_users
                                self.headers = temp_headers
                                self.headersHidden = temp_headers_hidden
                                self.currentFile = old_file
                                self.read_Sections = old_read_sections
                                self.config.save_currentFile(self.currentFile)
                                self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                                return False
                            else:
                                continue_anyway = msg.checkBox().isChecked()
                else:
                    msg = QMessageBox()
                    msg.addButton("Ja", QMessageBox.YesRole)
                    msg.addButton("Nein", QMessageBox.NoRole)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Warnung")
                    msg.setText("Die Header-Länge stimmen nicht überein")
                    msg.setInformativeText('Der Header-ist kürzer/länger als die Vorgabe')
                    if msg.exec_():
                        print("Cancel")
                        self.users = temp_users
                        self.headers = temp_headers
                        self.headersHidden = temp_headers_hidden
                        self.currentFile = old_file
                        self.read_Sections = old_read_sections
                        self.config.save_currentFile(self.currentFile)
                        self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                        return False
                    for x in range(len(fields) - len(self.read_Sections)):
                        self.read_Sections.append(ErrorMessage())
                continue_anyway = False
                for row in reader:
                    user = []
                    no_error: int = 0
                    user.append(0)
                    for x2, field in enumerate(fields):
                        checked = self.read_Sections[x2].is_value_allowed(row[field])
                        if checked != "Ok":
                            if not continue_anyway:
                                msg = QMessageBox()
                                msg.addButton("Ja", QMessageBox.YesRole)
                                msg.addButton("Nein", QMessageBox.NoRole)
                                msg.setIcon(QMessageBox.Warning)
                                msg.setWindowTitle("Warnung")
                                msg.setText("Die Daten sind sind fehlerhaft.\n Möchten Sie dennoch laden?")
                                msg.setInformativeText('Der Datensatz "' + row[field] + '" in Spalte: ' + str(
                                    x2) + " ist Fehlerhaft.\n" + checked)
                                cb = QCheckBox("Alle ignorieren")
                                msg.setCheckBox(cb)
                                if msg.exec_():
                                    print("Cancel")
                                    self.users = temp_users
                                    self.headers = temp_headers
                                    self.headersHidden = temp_headers_hidden
                                    self.currentFile = old_file
                                    self.read_Sections = old_read_sections
                                    self.config.save_currentFile(self.currentFile)
                                    self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                                    return False
                                else:
                                    continue_anyway = msg.checkBox().isChecked()
                            no_error += 1
                            user.append([row[field], checked])
                        else:
                            user.append(row[field])
                        user[0] = no_error
                    self.users.append(user)

                for fieldcount, field in enumerate(fields):
                    self.headers.append(field)
                    if not self.read_Sections[fieldcount].hide:
                        self.headersHidden.append(field)
                self.countLines = len(self.users) - 1
                self.config.save_currentFile(self.currentFile)
                self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                return True
        except Exception as e:
            print(e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Fehler")
            msg.setText("Die Datei konnten nicht geladen werden.")
            msg.setInformativeText('Möglicher Weise ist die Kodierung nicht ' + encoding_temp)
            msg.exec_()
            self.users = temp_users
            self.headers = temp_headers
            self.headersHidden = temp_headers_hidden
            self.currentFile = old_file
            self.config.save_currentFile(self.currentFile)
            self.setWindowTitle(self.currentFile + " - CSV_VaTa")
            return False

    def file_loaded(self) -> bool:
        if self.currentFile == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Fehler")
            msg.setText("Es ist keine Datei geladen")
            msg.setInformativeText("Bitte laden Sie zuerst eine Datei")
            msg.exec_()
            return False
        return True


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = UiMainWindow()

    sys.exit(app.exec_())
