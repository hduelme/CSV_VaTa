import csv
import config
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Message import Message

#import time

class my_QComboBox(QComboBox):
    def __init__(self,row,column):
        self.row = row
        self.column = column
        super().__init__()


class Error_Message(Message):
    def __init__(self):
        self.hide = False
        self.comboBox = False
        self.description =""

    def isvalueAllowed(self,value):
        return "Spalte zu viel"

class Ui_MainWindow(QMainWindow):


    def __init__(self):
            super().__init__()
            #contains no_error bool [0]
            #users (values) [1-x]
            #if error users [value, error]
            self.users = []
            self.headers = []
            self.headersHidden=[]
            self.countLines = 0

            self.pages = 0
            self.currentPage = 0
            self.currentFile =""
            self.hideCols = False
            self.allowComboBox = True

            self.onCheck = False


            self.config = config.Config()
            self.config.read_Config()
            self.read_Sections = self.config.read_Sections.copy()
            self.lines_Site = self.config.linesperpage
            self.setupUi()

            #try read last file
            file = self.config.lastFile
            if(os.path.isfile(file)):
                if (self.csv_load(file)):
                    self.calcPages()
                    self.setCurrentPage(0, self.lines_Site)
            else:
                self.currentFile=""
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
        newFile = QAction("New File from config",self)
        newFile.setShortcut('Ctrl+N')
        newFile.triggered.connect(self.newPageFromConfig)
        file.addAction(newFile)
        open = QAction("Open File",self)
        open.setShortcut('Ctrl+O')
        open.triggered.connect(self.chooseFile)
        file.addAction(open)
        save = QAction("&Save File",self)
        save.setShortcut('Ctrl+S')
        save.triggered.connect(self.FilesaveS)
        file.addAction(save)
        saveAs = QAction("&Save as File", self)
        saveAs.setShortcut('Ctrl+Shift+S')
        saveAs.triggered.connect(self.FilesaveAS)
        file.addAction(saveAs)
        edit = menubar.addMenu("Edit")
        add = QAction("&New line",self)
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
        docBottom = QDockWidget("Bottom",self)
        docBottom.setAllowedAreas(Qt.BottomDockWidgetArea)
        docBottom.setWidget(colum)
        docBottom.setFixedHeight(75)
        self.addDockWidget(Qt.BottomDockWidgetArea,docBottom)

        # show Window
        self.show()

    def allow_comboBox(self):
        if (self.fileLoaded()):
            sender = self.sender()
            #self.saveCurrentPage()
            self.allowComboBox = not self.allowComboBox
            if (self.allowComboBox):
                sender.setText("Hide ComboBoxes")
            else:
                sender.setText("Show ComboBoxes")
            self.setCurrentPage((self.currentPage ) * self.lines_Site, (self.currentPage+1) * self.lines_Site)

    def hideUnusedColums(self):
        if(self.fileLoaded()):
            sender = self.sender()

            #self.saveCurrentPage()
            self.hideCols = not self.hideCols
            if(self.hideCols):
                sender.setText("Unhide unused colums")
            else:
                sender.setText("Hide unused colums")
            self.setCurrentPage((self.currentPage) * self.lines_Site, (self.currentPage+1) * self.lines_Site)

    def addNewLine(self):
        if (self.fileLoaded()):
            #self.saveCurrentPage()
            user = [0]
            for x in range(0, len(self.headers)):
                checked = self.read_Sections[x].isvalueAllowed(self.read_Sections[x].defaultvalues)
                if(checked=="Ok"):
                    user.append(self.read_Sections[x].defaultvalues)
                else:
                    value = []
                    value.append(self.read_Sections[x].defaultvalues)
                    value.append(checked)
                    user.append(value)
                    user[0]+=1


            self.users.append(user)
            self.countLines = len(self.users)-1
            self.calcPages()
            self.currentPage = self.pages-1
            self.lcd_current_Page.display(str(self.currentPage + 1))
            self.setCurrentPage((self.pages-1) * self.lines_Site, (self.pages) * self.lines_Site)

    def vorPage(self):
        if (self.fileLoaded()):
            if(self.currentPage<self.pages-1):
                #self.saveCurrentPage()
                self.setCurrentPage((self.currentPage+1) * self.lines_Site, (self.currentPage + 2) * self.lines_Site)
                self.currentPage += 1
                self.lcd_current_Page.display(str(self.currentPage + 1))

    def backPage(self):
        if (self.fileLoaded()):
            if(self.currentPage>0):
                #self.saveCurrentPage()
                self.setCurrentPage((self.currentPage-1) * self.lines_Site, (self.currentPage) * self.lines_Site)
                self.currentPage -= 1
                self.lcd_current_Page.display(str(self.currentPage + 1))

    def initPage(self,file):
        if(self.csv_load(file)):
            self.calcPages()
            self.setCurrentPage(0, self.lines_Site)

    def newPageFromConfig(self):
        ok=False
        self.read_Sections = self.config.read_Sections.copy()
        if(self.currentFile!=""):
            msg = QMessageBox()
            msg.addButton("Ja", QMessageBox.YesRole)
            msg.addButton("Nein", QMessageBox.NoRole)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warnung")
            msg.setText("Achtung")
            msg.setInformativeText("Das erstellen einer neuen Datei verwirft alle Änderungen.\nMöchten Sie dennoch laden?")
            bttn = msg.exec_()
            if (not bttn):
                ok=True
        else:
            ok = True
        if(ok):
            self.headers = []
            self.headersHidden = []
            for section in self.read_Sections:
                self.headers.append(section.name)
                if(not section.hide):
                    self.headersHidden.append(section.name)
            self.users=[]
            self.countLines = len(self.users)-1
            self.calcPages()
            self.setCurrentPage(0, 0)
            self.currentFile = " "



    def calcPages(self):
        self.pages= int(self.countLines / self.lines_Site) + 1
        if(self.lines_Site>0):
            self.lcd_current_Page.display("1")
            self.lcd_max_Page.display(str(self.pages))


    def setCurrentPage(self,fr,to):
        #t1 = 0
        #for r in range(0,self.tableWidget.rowCount()):
            #self.tableWidget.removeRow(r)
        #start = time.time()
        self.tableWidget = QTableWidget()

        self.setCentralWidget(self.tableWidget)
        if (self.hideCols):
            self.tableWidget.setColumnCount(len(self.headersHidden))

        else:
            self.tableWidget.setColumnCount(len(self.headers))

        if(to>self.countLines):
            self.tableWidget.setRowCount(1+self.countLines-fr)

        else:
            self.tableWidget.setRowCount(self.lines_Site)
        vertikalHeader = []
        t1 = 0

        for allowed_value in range(fr,to):
            if(allowed_value<len(self.users)):
                user = self.users[allowed_value]
                skipped = 0
                if(user[0]==0):
                    for i in range(len(user)-1):
                        section = self.read_Sections[i]
                        if (section.hide and self.hideCols):
                            skipped += 1
                        else:
                            if(self.allowComboBox and section.comboBox):
                                index = -1
                                x = 0
                                comboBox = my_QComboBox(t1, i - skipped)
                                comboBox.setStyleSheet("QComboBox"
                                                       "{"
                                                       "background-color : white;"
                                                       "}")
                                comboBox.setToolTip("Description: " + section.description)

                                for allowed in section.allowedvalues:
                                    comboBox.addItem(allowed)
                                    if(allowed==user[i+1]):
                                        index = x
                                    x+=1

                                comboBox.setEditable(False)
                                if(index==-1):
                                    index=comboBox.count()
                                    model = comboBox.model()
                                    item = QStandardItem()
                                    item.setText(user[i+1])

                                    item.setBackground(QColor(255, 0, 0))
                                    model.appendRow(item)
                                comboBox.setCurrentIndex(index)
                                comboBox.currentIndexChanged.connect(self.save_ComboBox)
                                self.tableWidget.setCellWidget(t1, i-skipped, comboBox)


                            else:
                                self.tableWidget.setItem(t1, i-skipped, QTableWidgetItem(user[i+1]))
                                self.tableWidget.item(t1, i-skipped).setToolTip("Description: " + section.description)
                else:
                    for i in range(len(user) - 1):
                        section = self.read_Sections[i]
                        if (section.hide and self.hideCols):
                            skipped += 1
                        else:
                            error: bool = False
                            if(isinstance(user[i+1],list)):
                                error = True
                                value = user[i+1][0]
                            else:
                                value = user[i+1]
                            if (self.allowComboBox and section.comboBox):
                                index = -1
                                x = 0
                                comboBox = my_QComboBox(t1, i - skipped)
                                for allowed in section.allowedvalues:
                                    comboBox.addItem(allowed)
                                    if (allowed == value):
                                        index = x
                                    x += 1

                                comboBox.setEditable(False)
                                if (index == -1):
                                    index = comboBox.count()
                                    model = comboBox.model()
                                    item = QStandardItem()
                                    item.setText(value)

                                    item.setBackground(QColor(255, 0, 0))
                                    model.appendRow(item)
                                comboBox.setCurrentIndex(index)
                                if (not error):
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
                                    comboBox.setToolTip("Description: " + section.description + "\n" + user[i+1][1])
                                    comboBox.currentIndexChanged.connect(self.save_ComboBox)
                                self.tableWidget.setCellWidget(t1, i - skipped, comboBox)


                            else:
                                self.tableWidget.setItem(t1, i - skipped, QTableWidgetItem(value))
                                if(error):
                                    self.tableWidget.item(t1, i - skipped).setBackground(QColor(255, 0, 0))
                                    self.tableWidget.item(t1, i - skipped).setToolTip(
                                        "Description: " + section.description + "\n" + user[i+1][1])

                                else:
                                    self.tableWidget.item(t1, i - skipped).setBackground(QColor(140, 140, 140))
                                    self.tableWidget.item(t1, i - skipped).setToolTip("Description: " + section.description)

            vertikalHeader.append(str(allowed_value))
            t1 +=1
        if(self.hideCols):
            self.tableWidget.setHorizontalHeaderLabels(self.headersHidden)
        else:
            self.tableWidget.setHorizontalHeaderLabels(self.headers)
        self.tableWidget.setVerticalHeaderLabels(vertikalHeader)
        self.tableWidget.itemChanged.connect(self.save_item)
        #print("Time: ",time.time()-start)
        #self.checkCurrentPage()

    def test(self):
        print("TESTT")

    def save_item(self, item):
        if(not self.onCheck):
            self.onCheck = True
            if(self.hideCols):
                count = 0
                for x in range(self.users[self.currentPage * self.config.linesperpage + item.row()]-1):
                    if(not self.read_Sections[x].hide):
                        count+=1
                    if(count==item.column()):
                        column = x
                        break
            else:
                current_column = item.column()
            testing = self.read_Sections[item.column()].isvalueAllowed(item.text())
            if(testing!="Ok"):
                self.tableWidget.item(item.row(), item.column()).setBackground(QColor(255, 0, 0))
                self.tableWidget.item(item.row(), item.column()).setToolTip("Description: " + self.read_Sections[current_column].description + "\n"+testing)
                value = []
                value.append(item.text())
                value.append(testing)
                if(not isinstance(self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1],list)):
                    self.users[self.currentPage * self.config.linesperpage + item.row()][0] += 1
                    if (self.users[self.currentPage * self.config.linesperpage + item.row()][0] == 1):
                        for column in range(
                                len(self.users[self.currentPage * self.config.linesperpage + item.row()]) - 1):
                            if (column != current_column):
                                if (self.allowComboBox and self.read_Sections[column].comboBox):
                                    comboBox = self.tableWidget.cellWidget(item.row(), column)
                                    comboBox.setStyleSheet("QComboBox"
                                                           "{"
                                                           "background-color : gray;"
                                                           "}")

                                else:
                                    self.tableWidget.item(item.row(), column).setBackground(QColor(140, 140, 140))
                self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1] = value


            else:

                if(isinstance(self.users[self.currentPage * self.config.linesperpage + item.row()][current_column+1],list)):
                    self.users[self.currentPage * self.config.linesperpage + item.row()][0] -= 1
                    self.tableWidget.item(item.row(), item.column()).setToolTip(
                        "Description: " + self.read_Sections[current_column].description)
                    if(self.users[self.currentPage * self.config.linesperpage + item.row()][0]==0):
                        for column in range(len(self.users[self.currentPage * self.config.linesperpage + item.row()]) - 1):
                            if (self.allowComboBox and self.read_Sections[column].comboBox):
                                comboBox = self.tableWidget.cellWidget(item.row(), column)
                                comboBox.setStyleSheet("QComboBox"
                                                       "{"
                                                       "background-color : white;"
                                                       "}")

                            else:
                                self.tableWidget.item(item.row(), column).setBackground(QColor(255, 255, 255))
                else:
                    self.tableWidget.item(item.row(), current_column).setBackground(QColor(140, 140, 140))
                self.users[self.currentPage * self.config.linesperpage + item.row()][current_column + 1] = item.text()
            self.onCheck = False

    def save_ComboBox(self):
        if (not self.onCheck):
            self.onCheck = True
            comboBox = self.sender()

            if (self.hideCols):
                count = 0
                for x in range(self.users[self.currentPage * self.config.linesperpage + comboBox.row] - 1):
                    if (not self.read_Sections[x].hide):
                        count += 1
                    if (count == comboBox.column):
                        column = x
                        break
            else:
                current_column = comboBox.column
            if(comboBox.currentIndex()+1<=len(self.read_Sections[current_column].allowedvalues)):
                if (isinstance( self.users[self.currentPage * self.config.linesperpage + comboBox.row][current_column+1],list)):
                    self.users[self.currentPage * self.config.linesperpage + comboBox.row][0]-=1

                    comboBox.setToolTip("Description: " + self.read_Sections[current_column].description)
                    if( self.users[self.currentPage * self.config.linesperpage + comboBox.row][0]==0):
                        for column in range(len(self.users[self.currentPage * self.config.linesperpage + comboBox.row]) - 1):
                            if (self.allowComboBox and self.read_Sections[column].comboBox):
                                comboBox_temp = self.tableWidget.cellWidget(comboBox.row, column)
                                comboBox_temp.setStyleSheet("QComboBox"
                                                       "{"
                                                       "background-color : white;"
                                                       "}")

                            else:
                                self.tableWidget.item(comboBox.row, column).setBackground(QColor(255, 255, 255))
                    else:
                        comboBox.setStyleSheet("QComboBox"
                                               "{"
                                               "background-color : gray;"
                                               "}")

                self.users[self.currentPage * self.config.linesperpage + comboBox.row][current_column+1]=comboBox.currentText()

            else:
                if (not isinstance(self.users[self.currentPage * self.config.linesperpage + comboBox.row][current_column + 1],list)):
                    comboBox.setStyleSheet("QComboBox"
                                                "{"
                                                "background-color : red;"
                                                "}")
                    comboBox.setToolTip("Description: " + self.read_Sections[current_column].description + "\nUnerlaubter Wert.")
                    self.users[self.currentPage * self.config.linesperpage + comboBox.row][0] += 1
                    if (self.users[self.currentPage * self.config.linesperpage + comboBox.row][0] == 1):
                        for column in range(len(self.users[self.currentPage * self.config.linesperpage + comboBox.row]) - 1):
                            if (column != current_column):
                                if (self.allowComboBox and self.read_Sections[column].comboBox):
                                    comboBox_temp = self.tableWidget.cellWidget(comboBox.row, column)
                                    comboBox_temp.setStyleSheet("QComboBox"
                                                           "{"
                                                           "background-color : gray;"
                                                           "}")

                                else:
                                    self.tableWidget.item(comboBox.row, column).setBackground(QColor(140, 140, 140))
                value = []
                value.append(comboBox.currentText())
                value.append("Uneralaubter Wert.")
                self.users[self.currentPage * self.config.linesperpage + comboBox.row][current_column + 1] = value
        self.onCheck = False

    def delline(self):
        if (self.fileLoaded()):
            if(self.tableWidget.rowCount()>0):
                i, okPressed = QInputDialog.getInt(self, "Get integer", "Line number:", self.tableWidget.currentRow(), 0, self.countLines, 1)
                if okPressed:
                    #self.saveCurrentPage()
                    self.users.pop(i)
                    if(self.countLines==0):
                        self.currentPage=0
                        self.lcd_current_Page.display("0")
                        self.lcd_max_Page.display("0")
                        self.tableWidget.removeRow(0)
                    else:
                        self.countLines = len(self.users) - 1
                        self.calcPages()
                        self.setCurrentPage((self.currentPage) * self.lines_Site, (self.currentPage + 1) * self.lines_Site)


    def FilesaveS(self):
        if (self.fileLoaded()):
            if(os.path.isfile(self.currentFile)):
                self.Filesave(self.currentFile)
            else:
                self.FilesaveAS()

    def Filesave(self,file):
        if(filter!=""):
            #self.saveCurrentPage()
            self.saveCSV(file)

    def FilesaveAS(self):
        if (self.fileLoaded()):
            filename = QFileDialog.getSaveFileName(
                self, self.tr('Import file'), '',
                '(*.csv);;' + self.tr('All files(*)'))
            if filename != ('', ''):
                self.Filesave(filename[0])

    def saveCSV(self,file):
        with open(file, 'w', newline='', encoding=self.config.encoding) as file:
            writer = csv.writer(file, delimiter=';', quotechar='"')
            writer.writerow(self.headers)
            continue_anyway = False

            for row in self.users:
                for x2 in range(1,len(row)):
                    if(row[0]>0):
                        if(isinstance(row[x2],list)and not continue_anyway):
                            msg = QMessageBox()
                            msg.addButton("Ja", QMessageBox.YesRole)
                            msg.addButton("Nein", QMessageBox.NoRole)
                            msg.setIcon(QMessageBox.Warning)
                            msg.setWindowTitle("Warnung")
                            msg.setText("Die Daten sind fehlerhaft\n Möchten Sie dennoch speichern?")
                            msg.setInformativeText(
                                'Der Datensatz in Zeile"' + str(x2) + '" in Spalte: "' +  self.headers[x2] + '" ist Fehlerhaft.\n'+row[x2][1])
                            cb = QCheckBox("Alle ignorieren")
                            msg.setCheckBox(cb)
                            bttn = msg.exec_()
                            if (bttn):
                                print("Cancel")
                                return False
                            else:
                                continue_anyway = msg.checkBox().isChecked()


            for row in self.users:
                out =[]
                for x in range(1,len(row)):
                    if(isinstance(row[x],list)):
                        out.append(row[x][0])
                    else:
                        out.append(row[x])
                writer.writerow(out)


    def chooseFile(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr('Import file'), '',
            '(*.csv);;' + self.tr('All files(*)'))
        if filename != ('', ''):

            self.initPage(filename[0])

    def csv_load(self,file):
        old_read_Sections = self.read_Sections.copy()
        self.read_Sections = self.config.read_Sections.copy()
        oldFile = self.currentFile
        self.currentFile=file
        tempUsers=self.users.copy()
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
                if(len(self.read_Sections)==len(fields)):
                    for x in range(len(fields)):
                        if (self.read_Sections[x].name != fields[x]and not continue_anyway):
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
                            if (bttn):
                                print("Cancel")
                                self.users=tempUsers
                                self.headers=tempHeaders
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
                    if (bttn):
                        print("Cancel")
                        self.users = tempUsers
                        self.headers = tempHeaders
                        self.headersHidden = tempHeadersHidden
                        self.currentFile = oldFile
                        self.read_Sections = old_read_Sections
                        self.config.save_currentFile(self.currentFile)
                        self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                        return False
                    for x in range(len(fields)-len(self.read_Sections)):
                        self.read_Sections.append(Error_Message())
                continue_anyway = False
                for row in reader:
                    user = []
                    x2=0
                    no_error: bool = 0
                    user.append(0)

                    for field in fields:
                        # print(row[field])
                        if(x2>len(self.config.read_Sections)-1):
                            print("Error")
                        checked = self.read_Sections[x2].isvalueAllowed(row[field])
                        if(checked!="Ok"):
                            if(not continue_anyway):
                                msg = QMessageBox()
                                msg.addButton("Ja", QMessageBox.YesRole)
                                msg.addButton("Nein", QMessageBox.NoRole)
                                msg.setIcon(QMessageBox.Warning)
                                msg.setWindowTitle("Warnung")
                                msg.setText("Die Daten sind sind fehlerhaft.\n Möchten Sie dennoch laden?")
                                msg.setInformativeText('Der Datensatz "'+row[field]+ '" in Spalte: '+str(x2)+" ist Fehlerhaft.\n"+checked)
                                cb = QCheckBox("Alle ignorieren")
                                msg.setCheckBox(cb)
                                bttn = msg.exec_()

                                if (bttn):
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
                            user.append([row[field],checked])
                        else:
                            user.append(row[field])
                        x2+=1
                        user[0]=no_error
                    self.users.append(user)

                for fieldcount,field in enumerate(fields):
                    self.headers.append(field)
                    if(not self.read_Sections[fieldcount].hide):
                        self.headersHidden.append(field)
                self.countLines = len(self.users)-1
                self.config.save_currentFile(self.currentFile)
                self.setWindowTitle(self.currentFile+" - CSV_VaTa")
                return True
        except Exception as e:
            print(e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Fehler")
            msg.setText("Die Datei konnten nicht geladen werden.")
            msg.setInformativeText('Möglicher Weise ist die Kodierung nicht '+encoding_temp)
            msg.exec_()
            self.users = tempUsers
            self.headers = tempHeaders
            self.headersHidden = tempHeadersHidden
            self.currentFile = oldFile
            self.config.save_currentFile(self.currentFile)
            self.setWindowTitle(self.currentFile + " - CSV_VaTa")
            return False


    def fileLoaded(self):
        if(self.currentFile==""):
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
    w = Ui_MainWindow()

    sys.exit(app.exec_())