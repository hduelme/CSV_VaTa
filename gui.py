import csv
import config
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_MainWindow(QMainWindow):


    def __init__(self):
            super().__init__()
            self.users = []
            self.headers = []
            self.headersHidden=[]
            self.countLines = 0

            self.pages = 0
            self.currentPage = 0
            self.currentFile =""
            self.hideCols = False
            self.allowComboBox = True


            self.config = config.Config()
            self.config.read_Config()
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
        check = QAction("&Check Page again",self)
        check.setShortcut('Ctrl+R')
        check.triggered.connect(self.checkCurrentPage)
        edit.addAction(check)

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
            self.saveCurrentPage()
            self.allowComboBox = not self.allowComboBox
            if (self.hideCols):
                sender.setText("Disable ComboBoxes")
            else:
                sender.setText("Allow ComboBoxes")
            self.setCurrentPage((self.currentPage ) * self.lines_Site, (self.currentPage+1) * self.lines_Site)

    def hideUnusedColums(self):
        if(self.fileLoaded()):
            sender = self.sender()

            self.saveCurrentPage()
            self.hideCols = not self.hideCols
            if(self.hideCols):
                sender.setText("Unhide unused colums")
            else:
                sender.setText("Hide unused colums")
            self.setCurrentPage((self.currentPage) * self.lines_Site, (self.currentPage+1) * self.lines_Site)

    def addNewLine(self):
        if (self.fileLoaded()):
            self.saveCurrentPage()
            toll = []
            for x in range(0, len(self.headers)):
                toll.append(self.config.read_Sections[x].defaultvalues)
            self.users.append(toll)
            self.countLines = len(self.users)-1
            self.calcPages()
            self.currentPage = self.pages-1
            self.lcd_current_Page.display(str(self.currentPage + 1))
            self.setCurrentPage((self.pages-1) * self.lines_Site, (self.pages) * self.lines_Site)

    def vorPage(self):
        if (self.fileLoaded()):
            if(self.currentPage<self.pages-1):
                self.saveCurrentPage()
                self.setCurrentPage((self.currentPage+1) * self.lines_Site, (self.currentPage + 2) * self.lines_Site)
                self.currentPage += 1
                self.lcd_current_Page.display(str(self.currentPage + 1))

    def backPage(self):
        if (self.fileLoaded()):
            if(self.currentPage>0):
                self.saveCurrentPage()
                self.setCurrentPage((self.currentPage-1) * self.lines_Site, (self.currentPage) * self.lines_Site)
                self.currentPage -= 1
                self.lcd_current_Page.display(str(self.currentPage + 1))

    def initPage(self,file):
        if(self.csv_load(file)):
            self.calcPages()
            self.setCurrentPage(0, self.lines_Site)

    def newPageFromConfig(self):
        ok=False
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
            for section in self.config.read_Sections:
                self.headers.append(section.name)
                if(section.hide=='False'):
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
                t2 = 0
                skipped = 0
                for i in user:
                    section = self.config.read_Sections[t2]
                    if (section.hide == "False" or not self.hideCols):
                        if(self.allowComboBox and section.comboBox):
                            index = -1
                            x = 0
                            data = []
                            for allowed in section.allowedvalues:
                                data.append(allowed)
                                if(allowed==i):
                                    index = x
                                x+=1

                            comboBox = QComboBox()
                            comboBox.addItems(data)
                            comboBox.setEditable(False)
                            if(index==-1):
                                index = len(data)
                                model = comboBox.model()
                                item = QStandardItem()
                                item.setText(i)

                                item.setBackground(QColor(255, 0, 0))
                                model.appendRow(item)
                            comboBox.setCurrentIndex(index)


                            self.tableWidget.setCellWidget(t1, t2-skipped, comboBox)


                        else:
                            self.tableWidget.setItem(t1, t2-skipped, QTableWidgetItem(i))
                    else:
                        skipped +=1
                    t2 += 1
            vertikalHeader.append(str(allowed_value))
            t1 +=1
        if(self.hideCols):
            self.tableWidget.setHorizontalHeaderLabels(self.headersHidden)
        else:
            self.tableWidget.setHorizontalHeaderLabels(self.headers)
        self.tableWidget.setVerticalHeaderLabels(vertikalHeader)
        self.checkCurrentPage()

    def checkCurrentPage(self):
        rows = self.tableWidget.rowCount()
        if (self.hideCols):
            count = len(self.headersHidden)
        else:
            count = len(self.headers)
        for row in range(rows):
            no_error = []
            combo_no_error = []
            x = 0
            skipped = 0
            temp_Sections = self.config.read_Sections
            for col in range(len(self.headers)):
                if (x < len(temp_Sections)):
                    if (temp_Sections[col].hide != "False" and self.hideCols):
                        skipped+=1
                    else:
                        col_temp = col-skipped
                        description = temp_Sections[col].description
                        if(self.allowComboBox and temp_Sections[col].comboBox):
                            comboBox = self.tableWidget.cellWidget(row, col_temp)
                            if(comboBox.currentIndex()+1<=len(temp_Sections[col].allowedvalues)):
                                combo_no_error.append(col_temp)
                                comboBox.setStyleSheet("QComboBox"
                                                       "{"
                                                       "background-color : white;"
                                                       "}")
                                comboBox.setToolTip("Description: "+description)

                            else:
                                comboBox.setStyleSheet("QComboBox"
                                                             "{"
                                                             "background-color : red;"
                                                             "}")
                                comboBox.setToolTip("Description: "+description+"\n"+"Unerlaubter Wert.")

                        else:
                            item = self.tableWidget.item(row, col_temp)
                            testing = temp_Sections[col].isvalueAllowed(item.text())

                            if(testing!="Ok"):
                                #print("Soll nicht so "+temp_Sections[col].name)
                                self.tableWidget.item(row, col_temp).setBackground(QColor(255, 0, 0))
                                self.tableWidget.item(row, col_temp).setToolTip("Description: "+description+"\n"+testing)

                            else:
                                self.tableWidget.item(row, col_temp).setBackground(QColor(255, 255, 255))
                                self.tableWidget.item(row, col_temp).setToolTip("Description: "+description)
                                no_error.append(col_temp)
                x+=1
            if((len(no_error)+len(combo_no_error))<count):
                for col_gray in no_error:
                        self.tableWidget.item(row, col_gray).setBackground(QColor(140, 140, 140))
                if(self.allowComboBox):
                    for col_gray in combo_no_error:
                        comboBox = self.tableWidget.cellWidget(row, col_gray)
                        comboBox.setStyleSheet("QComboBox"
                                               "{"
                                               "background-color : gray;"
                                               "}")

    def delline(self):
        if (self.fileLoaded()):
            if(self.tableWidget.rowCount()>0):
                i, okPressed = QInputDialog.getInt(self, "Get integer", "Percentage:", self.tableWidget.currentRow(), 0, self.countLines, 1)
                if okPressed:
                    self.saveCurrentPage()
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
            self.saveCurrentPage()
            self.saveCSV(file)

    def FilesaveAS(self):
        if (self.fileLoaded()):
            filename = QFileDialog.getSaveFileName(
                self, self.tr('Import file'), '',
                '(*.csv);;' + self.tr('All files(*)'))
            if filename != ('', ''):
                self.Filesave(filename[0])


    def saveCurrentPage(self):
        rows = self.tableWidget.rowCount()
        for row in range (rows):
            user = []
            skipped = 0
            for col in range (len(self.headers)):
                if(self.config.read_Sections[col].hide !="False" and self.hideCols):
                    user.append(self.users[(self.currentPage * self.lines_Site) + row][col])
                    skipped += 1
                else:
                    col_temp = col-skipped
                    if(self.allowComboBox and self.config.read_Sections[col].comboBox):
                        comboBox = self.tableWidget.cellWidget(row, col_temp)
                        user.append(comboBox.currentText())
                    else:
                        item=self.tableWidget.item(row,col_temp)
                        user.append(item.text())
            if(len(user)>len(self.headers)):
                print("Länge FALSCH")
            self.users[(self.currentPage * self.lines_Site) + row]=user

    def saveCSV(self,file):
        with open(file, 'w', newline='', encoding=self.config.encoding) as file:
            writer = csv.writer(file, delimiter=';', quotechar='"')
            writer.writerow(self.headers)
            continue_anyway = False
            for row in self.users:
                for x2 in range(len(row)):
                    if (x2 < len(self.config.read_Sections)):
                        checked = self.config.read_Sections[x2].isvalueAllowed(row[x2])
                        if (checked != "Ok"and not continue_anyway):
                            msg = QMessageBox()
                            msg.addButton("Ja", QMessageBox.YesRole)
                            msg.addButton("Nein", QMessageBox.NoRole)
                            msg.setIcon(QMessageBox.Warning)
                            msg.setWindowTitle("Warnung")
                            msg.setText("Die Daten sind fehlerhaft\n Möchten Sie dennoch speichern?")
                            msg.setInformativeText(
                                'Der Datensatz in Zeile"' + str(x2) + '" in Spalte: "' +  self.config.read_Sections[x2].name + '" ist Fehlerhaft.\n'+checked)
                            cb = QCheckBox("Alle ignorieren")
                            msg.setCheckBox(cb)
                            bttn = msg.exec_()
                            if (bttn):
                                print("Cancel")
                                return False
                            else:
                                continue_anyway = msg.checkBox().isChecked()

            for row in self.users:
                writer.writerow(row)


    def chooseFile(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr('Import file'), '',
            '(*.csv);;' + self.tr('All files(*)'))
        if filename != ('', ''):

            self.initPage(filename[0])

    def csv_load(self,file):
        oldFile = self.currentFile
        self.currentFile=file
        tempUsers=self.users
        tempHeaders = self.headers
        tempHeadersHidden = self.headersHidden
        self.headers = []
        self.users = []
        encoding_temp = self.config.encoding
        try:
            with open(file, newline='', encoding=encoding_temp) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
                fields = reader.fieldnames

                print(fields)
                continue_anyway = False
                if(len(self.config.read_Sections)==len(fields)):
                    for x in range(len(fields)):
                        if (self.config.read_Sections[x].name != fields[x]and not continue_anyway):
                            print("warnung nicht gleich")
                            msg = QMessageBox()
                            msg.addButton("Ja", QMessageBox.YesRole)
                            msg.addButton("Nein", QMessageBox.NoRole)
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Die Header stimmen nicht überein")
                            msg.setInformativeText('Der Header "' + fields[x] + '" sollte "' + self.config.read_Sections[
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
                        self.config.save_currentFile(self.currentFile)
                        self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                        return False
                continue_anyway = False
                for row in reader:
                    user = []
                    x2=0
                    for field in fields:
                        # print(row[field])
                        if(x2<len(self.config.read_Sections)):
                            checked = self.config.read_Sections[x2].isvalueAllowed(row[field])
                            if(checked!="Ok" and not continue_anyway):
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
                                    self.config.save_currentFile(self.currentFile)
                                    self.setWindowTitle(self.currentFile + " - CSV_VaTa")
                                    return False
                                else:
                                    continue_anyway = msg.checkBox().isChecked()
                            user.append(row[field])
                            x2+=1
                        else:
                            print("Spalte zu viel")


                    self.users.append(user)
                fieldcount = 0
                for field in fields:
                    self.headers.append(field)
                    if(self.config.read_Sections[fieldcount].hide=="False"):
                        self.headersHidden.append(field)
                    fieldcount +=1
                for row in reader:
                    user = []
                    for field in fields:
                        user.append(row[field])

                    self.users.append(user)
                self.countLines = len(self.users)-1
                self.config.save_currentFile(self.currentFile)
                self.setWindowTitle(self.currentFile+" - CSV_VaTa")
                return True
        except:
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