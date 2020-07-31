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

    def isvalueAllowed(self, value):
        return "Spalte zu viel"


class UiMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
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
        self.setupUi()

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

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1200, 1000)
        self.setWindowIcon(QIcon("./logo.png"))
        self.setWindowTitle("CSV_VaTa")
        self.setAcceptDrops(False)

        # Init menubar
        menubar = self.menuBar()
        file = menubar.addMenu("File")
        newFile = QAction("New File from config", self)
        newFile.setShortcut('Ctrl+N')
        newFile.triggered.connect(self.newPageFromConfig)
        file.addAction(newFile)
        open = QAction("Open File", self)
        open.setShortcut('Ctrl+O')
        open.triggered.connect(self.chooseFile)
        file.addAction(open)
        save = QAction("&Save File", self)
        save.setShortcut('Ctrl+S')
        save.triggered.connect(self.FilesaveS)
        file.addAction(save)
        saveAs = QAction("&Save as File", self)
        saveAs.setShortcut('Ctrl+Shift+S')
        saveAs.triggered.connect(self.FilesaveAS)
        file.addAction(saveAs)
        edit = menubar.addMenu("Edit")
        add = QAction("&New line", self)
        add.setShortcut('Insert')
        add.triggered.connect(self.addNewLine)
        edit.addAction(add)

        delline = QAction("&Delete Line", self)
        delline.setShortcut('Delete')
        delline.triggered.connect(self.delline)
        edit.addAction(delline)
        """
        check = QAction("&Check Page again",self)
        check.setShortcut('Ctrl+R')
        check.triggered.connect(self.checkCurrentPage)
        edit.addAction(check)
        """

        hideColums = QAction("Hide unused colums", self)
        hideColums.setShortcut('Ctrl+H')
        hideColums.triggered.connect(self.hideUnusedColums)
        edit.addAction(hideColums)

        allowCombo = QAction("Disable ComboBoxes", self)
        allowCombo.triggered.connect(self.allow_comboBox)
        edit.addAction(allowCombo)

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

        colum = QOpenGLWidget()

        colum.setLayout(self.horizontalLayout)
        docBottom = QDockWidget("Bottom", self)
        docBottom.setAllowedAreas(Qt.BottomDockWidgetArea)
        docBottom.setWidget(colum)
        docBottom.setFixedHeight(75)
        self.addDockWidget(Qt.BottomDockWidgetArea, docBottom)

        # show Window
        self.show()

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
                checked = section.isvalueAllowed(section.default_values)
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
            bttn = msg.exec_()
            if not bttn:
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
        vertikalHeader = []

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
                                x = 0
                                comboBox = MyQComboBox(row, i - skipped)
                                comboBox.setStyleSheet("QComboBox"
                                                       "{"
                                                       "background-color : white;"
                                                       "}")
                                comboBox.setToolTip("Description: " + section.description)

                                for x, allowed in enumerate(section.allowed_values):
                                    comboBox.addItem(allowed)
                                    if allowed == value_user:
                                        index = x

                                comboBox.setEditable(False)
                                if index == -1:
                                    index = comboBox.count()
                                    model = comboBox.model()
                                    item = QStandardItem()
                                    item.setText(value_user)
                                    item.setBackground(QColor(255, 0, 0))
                                    model.appendRow(item)
                                comboBox.setCurrentIndex(index)
                                comboBox.currentIndexChanged.connect(self.save_ComboBox)
                                self.tableWidget.setCellWidget(row, i - skipped, comboBox)


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
                                x = 0
                                comboBox = MyQComboBox(row, i - skipped)
                                for x, allowed in enumerate(section.allowed_values):
                                    comboBox.addItem(allowed)
                                    if allowed == value:
                                        index = x

                                comboBox.setEditable(False)
                                if index == -1:
                                    index = comboBox.count()
                                    model = comboBox.model()
                                    item = QStandardItem()
                                    item.setText(value)

                                    item.setBackground(QColor(255, 0, 0))
                                    model.appendRow(item)
                                comboBox.setCurrentIndex(index)
                                if not error:
                                    comboBox.setStyleSheet("QComboBox"
                                                           "{"
                                                           "background-color : gray;"
                                                           "}")
                                    comboBox.setToolTip("Description: " + section.description)

                                else:
                                    comboBox.setStyleSheet("QComboBox"
                                                           "{"
                                                           "background-color : red;"
                                                           "}")
                                    comboBox.setToolTip("Description: " + section.description + "\n" + value_user[1])
                                    comboBox.currentIndexChanged.connect(self.save_ComboBox)
                                self.tableWidget.setCellWidget(row, i - skipped, comboBox)


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

            vertikalHeader.append(str(allowed_value))
        if self.hideCols:
            self.tableWidget.setHorizontalHeaderLabels(self.headersHidden)
        else:
            self.tableWidget.setHorizontalHeaderLabels(self.headers)
        self.tableWidget.setVerticalHeaderLabels(vertikalHeader)
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
            testing = self.read_Sections[item.column()].isvalueAllowed(item.text())
            if testing != "Ok":
                self.tableWidget.item(item.row(), item.column()).setBackground(QColor(255, 0, 0))
                self.tableWidget.item(item.row(), item.column()).setToolTip(
                    "Description: " + self.read_Sections[current_column].description + "\n" + testing)
                value = []
                value.append(item.text())
                value.append(testing)
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
                                        comboBox = self.tableWidget.cellWidget(item.row(), column - skipped)
                                        comboBox.setStyleSheet("QComboBox"
                                                               "{"
                                                               "background-color : gray;"
                                                               "}")

                                    else:
                                        self.tableWidget.item(item.row(), column - skipped).setBackground(
                                            QColor(140, 140, 140))
                self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1] = value


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
                                    comboBox = self.tableWidget.cellWidget(item.row(), column - skipped)
                                    comboBox.setStyleSheet("QComboBox"
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
            comboBox = self.sender()

            if self.hideCols:
                count = 0
                for column, section in enumerate(self.read_Sections):
                    if count == comboBox.column:
                        current_column = column
                        break
                    if not section.hide:
                        count += 1
            else:
                current_column = comboBox.column
            if comboBox.currentIndex() + 1 <= len(self.read_Sections[current_column].allowed_values):
                if (
                isinstance(self.users[self.currentPage * self.config.linesperpage + comboBox.row][current_column + 1],
                           list)):
                    self.users[self.currentPage * self.config.linesperpage + comboBox.row][0] -= 1

                    comboBox.setToolTip("Description: " + self.read_Sections[current_column].description)
                    if self.users[self.currentPage * self.config.linesperpage + comboBox.row][0] == 0:
                        skipped = 0
                        for column, section in enumerate(self.read_Sections):
                            if section.hide and self.hideCols:
                                skipped += 1
                            else:
                                if self.allowComboBox and section.comboBox:
                                    comboBox_temp = self.tableWidget.cellWidget(comboBox.row, column - skipped)
                                    comboBox_temp.setStyleSheet("QComboBox"
                                                                "{"
                                                                "background-color : white;"
                                                                "}")

                                else:
                                    self.tableWidget.item(comboBox.row, column - skipped).setBackground(
                                        QColor(255, 255, 255))
                    else:
                        comboBox.setStyleSheet("QComboBox"
                                               "{"
                                               "background-color : gray;"
                                               "}")

                self.users[self.currentPage * self.config.linesperpage + comboBox.row][
                    current_column + 1] = comboBox.currentText()

            else:
                if (not isinstance(
                        self.users[self.currentPage * self.config.linesperpage + comboBox.row][current_column + 1],
                        list)):
                    comboBox.setStyleSheet("QComboBox"
                                           "{"
                                           "background-color : red;"
                                           "}")
                    comboBox.setToolTip(
                        "Description: " + self.read_Sections[current_column].description + "\nUnerlaubter Wert.")
                    self.users[self.currentPage * self.config.linesperpage + comboBox.row][0] += 1
                    if self.users[self.currentPage * self.config.linesperpage + comboBox.row][0] == 1:
                        skipped = 0
                        for column, section in enumerate(self.read_Sections):
                            if section.hide and self.hideCols:
                                skipped += 1
                            else:
                                if column - skipped != current_column:
                                    if self.allowComboBox and section.comboBox:
                                        comboBox_temp = self.tableWidget.cellWidget(comboBox.row, column - skipped)
                                        comboBox_temp.setStyleSheet("QComboBox"
                                                                    "{"
                                                                    "background-color : gray;"
                                                                    "}")

                                    else:
                                        self.tableWidget.item(comboBox.row, column - skipped).setBackground(
                                            QColor(140, 140, 140))
                value = []
                value.append(comboBox.currentText())
                value.append("Uneralaubter Wert.")
                self.users[self.currentPage * self.config.linesperpage + comboBox.row][current_column + 1] = value
        self.onCheck = False

    def delline(self):
        if self.file_loaded():
            if self.tableWidget.rowCount() > 0:
                i, okPressed = QInputDialog.getInt(self, "Get integer", "Line number:", self.tableWidget.currentRow(),
                                                   0, self.countLines, 1)
                if okPressed:
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

    def FilesaveS(self):
        if self.file_loaded():
            if os.path.isfile(self.currentFile):
                self.Filesave(self.currentFile)
            else:
                self.FilesaveAS()

    def Filesave(self, file):
        if filter != "":
            self.saveCSV(file)

    def FilesaveAS(self):
        if self.file_loaded():
            filename = QFileDialog.getSaveFileName(
                self, self.tr('Import file'), '',
                '(*.csv);;' + self.tr('All files(*)'))
            if filename != ('', ''):
                self.Filesave(filename[0])

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
                            bttn = msg.exec_()
                            if bttn:
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
        old_read_Sections = self.read_Sections.copy()
        self.read_Sections = self.config.read_Sections.copy()
        oldFile = self.currentFile
        self.currentFile = file
        tempUsers = self.users.copy()
        tempHeaders = self.headers.copy()
        tempHeadersHidden = self.headersHidden.copy()
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
                            bttn = msg.exec_()
                            if bttn:
                                print("Cancel")
                                self.users = tempUsers
                                self.headers = tempHeaders
                                self.headersHidden = tempHeadersHidden
                                self.currentFile = oldFile
                                self.read_Sections = old_read_Sections
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
                    bttn = msg.exec_()
                    if bttn:
                        print("Cancel")
                        self.users = tempUsers
                        self.headers = tempHeaders
                        self.headersHidden = tempHeadersHidden
                        self.currentFile = oldFile
                        self.read_Sections = old_read_Sections
                        self.config.save_currentFile(self.currentFile)
                        self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                        return False
                    for x in range(len(fields) - len(self.read_Sections)):
                        self.read_Sections.append(ErrorMessage())
                continue_anyway = False
                for row in reader:
                    user = []
                    no_error: bool = 0
                    user.append(0)
                    for x2, field in enumerate(fields):
                        checked = self.read_Sections[x2].isvalueAllowed(row[field])
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
                                bttn = msg.exec_()

                                if bttn:
                                    print("Cancel")
                                    self.users = tempUsers
                                    self.headers = tempHeaders
                                    self.headersHidden = tempHeadersHidden
                                    self.currentFile = oldFile
                                    self.read_Sections = old_read_Sections
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
            self.users = tempUsers
            self.headers = tempHeaders
            self.headersHidden = tempHeadersHidden
            self.currentFile = oldFile
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
