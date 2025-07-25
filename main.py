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
            self.wobuttonlayout = QHBoxLayout()
            self.wobuttonlayout.setContentsMargins(20, 0, 20, 0)

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
            self.wobuttonlayout.addWidget(self.workorderOpen)

            self.woopenback = QPushButton("Back")
            self.woopenback.clicked.connect(self.ReturnToMain)
            self.wobuttonlayout.addWidget(self.woopenback)

            openlayout.addLayout(self.wobuttonlayout)
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

        self.dielectric_passed = [False, False]
        self.dielectric_failed = [False, False]
        self.dielectric_completed = False

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.dielectrictestbuttonlayout = QHBoxLayout()


        self.scroll = QScrollArea()
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll.setStyleSheet("""
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
        self.scroll.setMinimumHeight(500)
        self.scroll.setMaximumWidth(1100)
        self.scroll.setWidgetResizable(True)

        self.dielectriclabel = QLabel("""
        Begin by removing side panel<br><br><br>
        <b>1. Disconnect the P1 connector from J1 connector on circuit board.</b><br><br>
        <b>2. Install IAS11003B circular box connector into power input.</b><br><br>
        <i>Confirm test box leads are connected to hipot tester.</i><br><br>
        <b>2a. Install red and black test box jumpers from C to H.<br><br>
        Turn on the QuadTech Guardian 2510 Hipot Tester and press start.<br><br>
        The tester will increase the voltage of the Hi Pot test set in increments of 250 to 500 volts per second<br>
        until 1500 volts are applied across test connection and maintain the voltage at the 1500 volt level for 60 seconds.</b><br><br>
        Press Begin to continue.<br><br>
        """)

        self.dielectriclabel.setTextFormat(Qt.TextFormat.RichText)
        self.dielectriclabel.setWordWrap(True)
        self.dielectriclabel.setStyleSheet("""
                    font-size: 18px;
                    padding-top: 50px;
                    padding-left: 50px;
                    padding-right: 50px;
                    padding-bottom: 50px;
                    """)
        self.dielectriclabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.dielectriclabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.dielectrictestbuttonlayout)
        try:
            self.dielectricbeginbutton = QPushButton("Begin", self)
            self.dielectricbeginbutton.setFixedWidth(200)
            self.dielectricbeginbutton.clicked.connect(self.Dielectric)
            self.dielectrictestbuttonlayout.addWidget(self.dielectricbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

        #-------------------------------------------------------------------- Phase Readings


        phaselayout = QHBoxLayout()
        #phaselayout.setContentsMargins(0, 100, 0, 0)

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

        #------------------------------------------------------- Resistance Check
        resistance = QWidget()

        self.resistance_passed = [False, False, False]
        self.resistance_failed = [False, False, False]
        self.resistance_completed = False
        self.current_resistance_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.resistancetestbuttonlayout = QHBoxLayout()

        self.scroll = QScrollArea()
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll.setStyleSheet("""
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
        self.scroll.setMinimumHeight(500)
        self.scroll.setMaximumWidth(1100)
        self.scroll.setWidgetResizable(True)

        self.resistancelabel = QLabel(
                                     "<b>Turn QuadTech Milliohm Meter on. <br><br>"
                                     "1. Check resistance from plug lead G to un-anodized brew shelf.</b><br><br> " 
                                     "<i> The millohm meter should not exceed 4.5 milliohms. </i><br><br>"
                                     )

        self.resistancelabel.setTextFormat(Qt.TextFormat.RichText)
        self.resistancelabel.setWordWrap(True)
        self.resistancelabel.setStyleSheet("""
                            font-size: 18px;
                            padding-top: 50px;
                            padding-left: 50px;
                            padding-right: 50px;
                            padding-bottom: 50px;
                            """)
        self.resistancelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.resistancelabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.resistancetestbuttonlayout)
        try:
            self.resistancebeginbutton = QPushButton("Begin", self)
            self.resistancebeginbutton.setFixedWidth(200)
            self.resistancebeginbutton.clicked.connect(self.Resistance)
            self.resistancetestbuttonlayout.addWidget(self.resistancebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

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

        resistance.setLayout(layout)
        self.tabs.addTab(resistance, f"Resistance")

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

    def Dielectric(self):


        try:
            if not self.dielectric_passed[0] and not self.dielectric_failed[0]:
                msg1 = QMessageBox()
                msg1.setWindowTitle("Check Current")
                msg1.setText("Current flow should not exceed a maximum of 2.0 milliamperes during the test period.")
                msg1.setIcon(QMessageBox.Icon.Information)

                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)

                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.dielectric_passed[0] = True
                    self.dielectric_failed[0] = False
                    self.updateDielectricStep()
                elif msg1.clickedButton() == fail_button:
                    self.dielectric_passed[0] = False
                    self.dielectric_failed[0] = True
                    self.updateDielectricStep()


            elif self.dielectric_passed[0] or self.dielectric_failed[0]:
                msg1 = QMessageBox()
                msg1.setWindowTitle("Check Current")
                msg1.setText("Does megaohmmeter read greater than 2?")
                msg1.setIcon(QMessageBox.Icon.Information)

                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)

                msg1.exec()


                if msg1.clickedButton() == pass_button:
                    self.dielectric_passed[1] = True
                    self.dielectric_failed[1] = False
                    self.dielectric_completed = True
                    self.updateDielectricStep()
                elif msg1.clickedButton() == fail_button:
                    self.dielectric_passed[1] = False
                    self.dielectric_failed[1] = True
                    self.updateDielectricStep()


            elif self.dielectric_completed:
                msg1 = QMessageBox()
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The dielectric test has been completed successfully.")
                msg1.setIcon(QMessageBox.Icon.Information)

                pass_button = msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)

                msg1.exec()

        except Exception as e:
            print(f"Error: {e}")

    def updateDielectricStep(self):
        if self.dielectric_passed[0] or self.dielectric_failed[0]:

            self.dielectriclabel.setText("<b>3. Connect QuadTech megohmmeter by connecting C and M jumpers on the test box.<br><br>"
                            "Set scale on megohmmeter to 500 volts and 100M.<br><br>"
                            "Turn megohmmeter power on.<br><br>"
                            "Flip switch to charge and then to measure.</b><br><br>"
                            "<i>The megohmmeter gauge must be greater than 2.</i><br><br>")



            self.dielectricbeginbutton.setText("Continue")
            self.dielectricbeginbutton.clicked.disconnect()
            self.dielectricbeginbutton.clicked.connect(self.Dielectric)

        if self.dielectric_passed[1] or self.dielectric_failed[1]:

            self.dielectriclabel.setText(
                                         "<b>The Dielectric Test is Completed!<br><br>"
                                         "Please flip the megohmmeter switch to discharge and then power off.<br><br>"
                                         "Disconnect IAS11003B circular box connector from the coffee maker.<br><br>"
                                         "Reconnect P1 connector to J1 connector on circuit board.</b><br><br>")

            self.dielectricbeginbutton.setText("Results")
            self.dielectricbeginbutton.clicked.disconnect()
            self.dielectricbeginbutton.clicked.connect(self.DielectricResults)

            self.dielectricrestart = QPushButton("Restart", self)
            self.dielectricrestart.clicked.connect(self.DielectricRestart)
            self.dielectricrestart.setFixedWidth(200)
            self.dielectrictestbuttonlayout.addWidget(self.dielectricrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def DielectricRestart(self):
        print("Restarting Dielectric Test")

    def DielectricResults(self):
        print("Printing Dielectric Test Results")

    def Resistance(self):
        try:
            msg1 = QMessageBox()
            msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_resistance_step == 0:
                msg1.setWindowTitle("Check Resistance")
                msg1.setText("Does the milliohm meter read equal to or less than 4.5 milliohms?")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.resistance_passed[0] = True
                    self.resistance_failed[0] = False
                    self.updateResistanceStep()
                    self.current_resistance_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.resistance_passed[0] = False
                    self.resistance_failed[0] = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_resistance_step == 1:
                msg1.setWindowTitle("Check Resistance")
                msg1.setText("Does the milliohm meter read equal to or less than 5.12 milliohms?")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.resistance_passed[1] = True
                    self.resistance_failed[1] = False
                    self.updateResistanceStep()
                    self.current_resistance_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.resistance_passed[1] = False
                    self.resistance_failed[1] = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_resistance_step == 2:
                msg1.setWindowTitle("Check Resistance")
                msg1.setText("Does the milliohm meter read equal to or less than 5.7 milliohms?")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.resistance_passed[2] = True
                    self.resistance_failed[2] = False
                    self.resistance_completed = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.resistance_passed[2] = False
                    self.resistance_failed[2] = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1

            # Completed
            elif self.resistance_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Resistance test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateResistanceStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateResistanceStep(self):
        if self.resistance_passed[0] or self.resistance_failed[0]:

            self.resistancelabel.setText(
                                "<b>2. If applicable, check the resistance from plug lead G to platen heater.</b><br><br>"
                                "<i>The milliohm meter should not exceed 5.12 milliohms.</i><br><br>"
                               )

            self.resistancebeginbutton.setText("Continue")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.Resistance)

        if self.resistance_passed[1] or self.resistance_failed[1]:

            self.resistancelabel.setText(
                                "<b>3. Connect a resistance bridge between plug lead F and faucet.</b><br><br>"
                                "<i>The milliohm meter should not exceed 5.7 milliohms.</i><br><br>"
                                )

            self.resistancebeginbutton.setText("Continue")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.Resistance)

        if self.resistance_passed[2] or self.resistance_failed[2]:
            self.resistancelabel.setText(
                                         "<b>Resistance Test Completed!</b><br><br>"
                                         "<b>Please Disconnect the IAS11003C plug from PP1 and turn off the milliohm meter.<br><br>"
                                        )
            self.resistancebeginbutton.setText("Results")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.ResistanceResults)

            self.resistancerestart = QPushButton("Restart", self)
            self.resistancerestart.clicked.connect(self.ResistanceRestart)
            self.resistancerestart.setFixedWidth(200)
            self.resistancetestbuttonlayout.addWidget(self.resistancerestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def ResistanceRestart(self):
        print("Restarting Insulation Test")

    def ResistanceResults(self):
        print("Printing Insulation Test Results")



# === Application entry point ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

