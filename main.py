import sys
import os

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
#from PyQt6.QtWidgets.QWidget import setWindowFlag

import pyvisa


# === Worker class in a thread ===
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def run(self):
        import time
        for i in range(5):
            self.progress.emit(f"Working... {i + 1}/5")
            time.sleep(1)
        self.finished.emit()


# === Main application window ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COMATS")
        #self.setFixedSize(800, 600)

        self.welcome = QWidget()
        self.setCentralWidget(self.welcome)

        self.welcomeLayout = QVBoxLayout()

        self.Logo = QPixmap("Images/InAir.png")
        self.logoLabel = QLabel()
        self.logoLabel.setStyleSheet("""
                    padding-top: 0px;
                    padding-bottom: 20px;
                    padding-left: 100px;
                    padding-right: 100px;
                        """)
        self.logoLabel.setScaledContents(True)
        self.logoLabel.setPixmap(self.Logo)
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcomeLayout.addWidget(self.logoLabel)


        self.welcomeLabel = QLabel("Welcome to COMATS")
        self.welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcomeLabel.setStyleSheet("""
                            padding-top: 50px;
                            padding-bottom: 50px;
                            padding-left: 100px;
                            padding-right: 100px;
                                """)
        self.welcomeLayout.addWidget(self.welcomeLabel)

        self.welcome.setLayout(self.welcomeLayout)


        # Temporary Globals:

        global phase1read
        global phase2read
        global phase3read

        self.createNewWorkorder = False
        self.editExistingWorkorder = False
        self.runIndividualTests = False
        self.runAllTests = False


        self.buttonLayout = QVBoxLayout()



        self.createworkorder = QPushButton("Create New Workorder")
        self.createworkorder.setFixedWidth(200)
        self.createworkorder.clicked.connect(self.CreateNewWorkorder)
        self.welcomeLayout.addWidget(self.createworkorder, alignment=Qt.AlignmentFlag.AlignCenter)

        self.openworkorder = QPushButton("Open Existing Workorder")
        self.openworkorder.setFixedWidth(200)
        self.openworkorder.clicked.connect(self.OpenExistingWorkorder)
        self.welcomeLayout.addWidget(self.openworkorder, alignment=Qt.AlignmentFlag.AlignCenter)
        self.welcomeLayout.addSpacing(100)


#--------------------------------------------------------------------------------- Creation/Edit Menu Buttons
    """ self.individual = QPushButton("Run Individual Tests")
        self.individual.clicked.connect(self.IndividualClicked)
        self.welcomeLayout.addWidget(self.individual)

        self.all = QPushButton("Run All Tests")
        self.all.clicked.connect(self.allClicked)
        self.welcomeLayout.addWidget(self.all) """

    def CreateNewWorkorder(self):
        try:
            self.createNewWorkorder = True
            self.setFixedSize(400, 200)

            self.workorderentry = QWidget()
            self.setCentralWidget(self.workorderentry)

            layout = QVBoxLayout()


            woentrylayout = QVBoxLayout()
            woentrylayout.setSpacing(5)

            wonumberlayout = QHBoxLayout()
            wonumberlayout.setContentsMargins(20, 0, 20, 0)


            woseriallayout = QHBoxLayout()
            woseriallayout.setContentsMargins(20, 0, 20, 0)

            wopartnumberlayout = QHBoxLayout()
            wopartnumberlayout.setContentsMargins(20, 0, 20, 0)

            techlayout = QHBoxLayout()
            techlayout.setContentsMargins(20, 0, 20, 0)

            wobuttonlayout = QHBoxLayout()
            wobuttonlayout.setContentsMargins(20, 0, 20, 0)


            self.workordernumber = QLabel("Workorder Number: ")
            wonumberlayout.addWidget(self.workordernumber)

            self.workordernumberfield = QLineEdit()
            self.workordernumberfield.setStyleSheet("""
                            QLineEdit {
                                border: none;
                                border-bottom: none;
                                outline: none;
                            }
                        """)
            self.workordernumberfield.setPlaceholderText("Enter workorder number...")
            wonumberlayout.addWidget(self.workordernumberfield)

            woentrylayout.addLayout(wonumberlayout)


            self.serialnumber = QLabel("Unit Serial Number:  ")
            woseriallayout.addWidget(self.serialnumber)

            self.serialnumberfield = QLineEdit()
            self.serialnumberfield.setStyleSheet("""
                QLineEdit {
                    border: none;
                    border-bottom: none;
                    outline: none;
                }
            """)
            self.serialnumberfield.setPlaceholderText("Enter serial number...")
            woseriallayout.addWidget(self.serialnumberfield)

            woentrylayout.addLayout(woseriallayout)

            self.unitpartnumber = QLabel("Unit Part Number:     ")
            wopartnumberlayout.addWidget(self.unitpartnumber)

            self.unitpartnumberfield = QLineEdit()
            self.unitpartnumberfield.setStyleSheet("""
                            QLineEdit {
                                border: none;
                                border-bottom: none;
                                outline: none;
                            }
                        """)
            self.unitpartnumberfield.setPlaceholderText("Enter part number...")
            wopartnumberlayout.addWidget(self.unitpartnumberfield)

            woentrylayout.addLayout(wopartnumberlayout)

            self.tech = QLabel("Technician:                 ")
            techlayout.addWidget(self.tech)

            self.techfield = QLineEdit()
            self.techfield.setStyleSheet("""
                            QLineEdit {
                                border: none;
                                border-bottom: none;
                                outline: none;
                            }
                        """)
            self.techfield.setPlaceholderText("Enter technician name...")
            techlayout.addWidget(self.techfield)

            woentrylayout.addLayout(techlayout)

            self.runallbutton = QPushButton("Run All Tests")
            self.runallbutton.clicked.connect(self.RunAllTests)
            wobuttonlayout.addWidget(self.runallbutton)

            self.runindbutton = QPushButton("Run Individual Tests")
            self.runindbutton.clicked.connect(self.RunIndividualTests)
            wobuttonlayout.addWidget(self.runindbutton)

            woentrylayout.addLayout(wobuttonlayout)


            layout.addLayout(woentrylayout)

            self.workorderentry.setLayout(layout)
        except Exception as e:
            print(f"Error as {e}")



    def OpenExistingWorkorder(self):
        try:
            self.openExistingWorkorder = True
            self.setFixedSize(200, 200)

            self.openWorkorder = QWidget()
            self.setCentralWidget(self.openWorkorder)

            layout = QVBoxLayout()
            layout.setSpacing(5)

            openlayout = QVBoxLayout()
            openlayout.setContentsMargins(20, 0, 20, 0)
            buttonlayout = QHBoxLayout()
            buttonlayout.setContentsMargins(20, 0, 20, 0)

            self.workordernumberfield = QLineEdit()
            self.workordernumberfield.setPlaceholderText("Enter workorder number...")
            self.workordernumberfield.setStyleSheet("""
                                        QLineEdit {
                                            border: none;
                                            border-bottom: none;
                                            outline: none;
                                        }
                                    """)
            openlayout.addWidget(self.workordernumberfield)

            self.workorderOpen = QPushButton("Open")
            self.workorderOpen.clicked.connect(self.RunIndividualTests)
            buttonlayout.addWidget(self.workorderOpen)

            self.woopenback = QPushButton("Back")
            self.woopenback.clicked.connect(self.ReturnToMain)
            buttonlayout.addWidget(self.woopenback)

            openlayout.addLayout(buttonlayout)
            layout.addLayout(openlayout)

            self.openWorkorder.setLayout(layout)

        except Exception as e:
            print(f"Error while opening workorder: {e}")


    def ReturnToMain(self):
        print("Return to main menu")


    def RunIndividualTests(self):
        self.runIndividualTests = True
        self.setFixedSize(1000, 600)


        workorder_file = f"{self.workordernumberfield.text()}.txt"
        test_path = os.path.join("Tests/", workorder_file)
        if not os.path.exists(test_path):
            with open(f"{test_path}", "w") as file:
                file.write(f"Workorder Number: {self.workordernumberfield.text()}\n"
                            f"Unit Serial Number: {self.serialnumberfield.text()}\n"
                            f"Part Number: {self.unitpartnumberfield.text()}\n"
                            f"Technician Name: {self.techfield.text()}\n\n\n")
        else:
            with open(f"{test_path}", "r") as file:
                print("You've opened an existing workorder!")

        phase1read = 0.57
        phase2read = 0.64
        phase3read = 0.59

        # Create QTabWidget
        if (self.runIndividualTests == True):
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)


        # Create 10 tabs

        #-------------------------------------------------------- Dielectric Test
        dielectric = QWidget()

        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll.setStyleSheet("""
                    QScrollArea {
        border: none;
        background-color: #f9f9f9;
    }

    QScrollBar:vertical {
        background: #eee;
        width: 12px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background: #999;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }

    QScrollBar:horizontal {
        background: #eee;
        height: 12px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background: #999;
        border-radius: 6px;
        min-width: 20px;
    }

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: none;
    }
        """)
        scroll.setMinimumHeight(500)
        scroll.setMaximumWidth(1100)
        scroll.setWidgetResizable(True)

        label = QLabel("""
        Begin by removing side panel<br><br><br>
        <b>1. Disconnect the P1 connector from J1 connector on circuit board.</b><br><br>
        <b>2. Install IAS11003B circular box connector into power input.</b><br><br>
        <i>Confirm test box leads are connected to hipot tester.</i><br><br>
        <b>2a. Install red and black test box jumpers from C to H.<br><br>
        Turn on the QuadTech Guardian 2510 Hipot Tester and press start.<br>
        The tester will increase the voltage of the Hi Pot test set in increments of 250 to 500 volts per second<br>
        until 1500 volts are applied across test connection and maintain the voltage at the 1500 volt level for 60 seconds.</b><br><br>
        Press Begin to continue.<br><br>
        """)

        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setStyleSheet("""
                    font-size: 18px;
                    padding-top: 50px;
                    padding-left: 50px;
                    padding-right: 50px;
                    padding-bottom: 50px;
                    """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(label)
        layout.addWidget(scroll)
        try:
            beginbutton = QPushButton("Begin", self)
            beginbutton.setFixedWidth(200)
            beginbutton.clicked.connect(self.BeginDielectric)
            layout.addWidget(beginbutton, alignment=Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            print(f"Error while opening workorder: {e}")


        """
        <b>3. Connect QuadTech megohmmeter by connecting C and M jumpers on the test box.<br><br>
        Set scale on megohmmeter to 500 volts and 100M.<br>
        Turn megohmmeter power on.<br>
        Flip switch to charge and then to measure.</b><br><br>
        <i>The megohmmeter gauge must be greater than 2.</i><br><br>
        <b>Flip megohmmeter switch to discharge and then turn power off.<br><br>
        Disconnect IAS11003B circular box connector from the coffee maker.<br>
        Reconnect P1 connector to J1 connector on circuit board.</b><br> """




        #-------------------------------------------------------------------- Phase Readings


        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(720, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)



        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)


        layout.addLayout(phaselayout)

        dielectric.setLayout(layout)
        self.tabs.addTab(dielectric, f"Dielectric")

        #------------------------------------------------------- Insulation Check
        insulation = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Insulation Check")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        insulation.setLayout(layout)
        self.tabs.addTab(insulation, f"Insulation")

        # ------------------------------------------------------- Leak Test
        leak = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Leak Check")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        leak.setLayout(layout)
        self.tabs.addTab(leak, f"Leak")

        # ------------------------------------------------------- Water Supply Temperature Test
        watertemp = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Water Supply Temperature Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        watertemp.setLayout(layout)
        self.tabs.addTab(watertemp, f"Water Supply Temp")

        # ------------------------------------------------------- Water Supply Temperature Test
        lamptest = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"ON/OFF and NO WATER Lamp Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        lamptest.setLayout(layout)
        self.tabs.addTab(lamptest, f"Lamp Test")

        # ------------------------------------------------------- Water Supply Temperature Test
        filltest = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Coffee Maker/Water Boiler Fill Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        filltest.setLayout(layout)
        self.tabs.addTab(filltest, f"Fill Test")

        # ------------------------------------------------------- Water Supply Temperature Test
        preheattest = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Preheat Time Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        preheattest.setLayout(layout)
        self.tabs.addTab(preheattest, f"Preheat Test")

        # ------------------------------------------------------- Water Supply Temperature Test
        heatertest = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Heater Operation Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        heatertest.setLayout(layout)
        self.tabs.addTab(heatertest, f"Heater Test")

        # ------------------------------------------------------- Water Supply Temperature Test
        teatest = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Tea Cycle Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        teatest.setLayout(layout)
        self.tabs.addTab(teatest, f"Tea Test")

        # ------------------------------------------------------- Water Supply Temperature Test
        hotplatetest = QWidget()
        layout = QVBoxLayout()

        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        label = QLabel(f"Hot Plate Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # -------------------------------------------------------------------- Phase Readings
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        hotplatetest.setLayout(layout)
        self.tabs.addTab(hotplatetest, f"Hot Plate Test")

    def RunAllTests(self):
        try:
            workorder_file = f"{self.workordernumberfield.text()}.txt"
            test_path = os.path.join("Tests/", workorder_file)
            if not os.path.exists(test_path):
                with open(f"{test_path}", "w") as file:
                    file.write(f"Workorder Number: {self.workordernumberfield.text()}\n"
                               f"Unit Serial Number: {self.serialnumberfield.text()}\n"
                               f"Part Number: {self.unitpartnumberfield.text()}\n"
                               f"Technician Name: {self.techfield.text()}\n\n\n")

            self.allTests = QWidget()
            self.setCentralWidget(self.allTests)
            self.layout = QVBoxLayout()

            self.allClicked = QLabel("Run All Test Programs.")
            self.layout.addWidget(self.allClicked)

            self.allTests.setLayout(self.layout)

        except Exception as e:
            print(f"Error: {e}")

    def BeginDielectric(self):
        try:
            msg1 = QMessageBox()
            msg1.setWindowTitle("Check Current")
            msg1.setText("Current flow shall not exceed a maximum of 2.0 milliamperes during the test period.")
            msg1.setIcon(QMessageBox.Icon.Information)

            pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
            fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)

            msg1.exec()

            if msg1.clickedButton() == pass_button:
                print("Test Passed")
            elif msg1.clickedButton() == fail_button:
                print("Test Failed")

            retval = msg1.exec()
            if retval == QMessageBox.StandardButton.Ok:
                print("OK pressed")
            else:
                print("Cancelled")
        except Exception as e:
            print(f"Error: {e}")





# === Application entry point ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

