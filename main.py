import sys
import os

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
#from PyQt6.QtWidgets.QWidget import setWindowFlag

#import pyvisa


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

        self.leak_passed = [False, False, False]
        self.leak_failed = [False, False, False]
        self.leak_completed = False
        self.current_leak_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.leaktestbuttonlayout = QHBoxLayout()

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

        self.leaklabel = QLabel(
            "<b>Leak step one. </b><br><br>"
             
            "<i> Leak step one condition </i><br><br>"
        )

        self.leaklabel.setTextFormat(Qt.TextFormat.RichText)
        self.leaklabel.setWordWrap(True)
        self.leaklabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.leaklabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.leaklabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.leaktestbuttonlayout)
        try:
            self.leakbeginbutton = QPushButton("Begin", self)
            self.leakbeginbutton.setFixedWidth(200)
            self.leakbeginbutton.clicked.connect(self.Leak)
            self.leaktestbuttonlayout.addWidget(self.leakbeginbutton,
                                                      alignment=Qt.AlignmentFlag.AlignCenter)

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

        leak.setLayout(layout)
        self.tabs.addTab(leak, f"Leak")

        # ------------------------------------------------------- Water Supply Temperature Test
        watertemp = QWidget()

        self.watertemp_passed = [False, False, False]
        self.watertemp_failed = [False, False, False]
        self.watertemp_completed = False
        self.current_watertemp_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.watertemptestbuttonlayout = QHBoxLayout()

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

        self.watertemplabel = QLabel(
            "<b>Water Supply Temperature step one. </b><br><br>"

            "<i> Water supply temperature step one condition </i><br><br>"
        )

        self.watertemplabel.setTextFormat(Qt.TextFormat.RichText)
        self.watertemplabel.setWordWrap(True)
        self.watertemplabel.setStyleSheet("""
                                            font-size: 18px;
                                            padding-top: 50px;
                                            padding-left: 50px;
                                            padding-right: 50px;
                                            padding-bottom: 50px;
                                            """)
        self.watertemplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.watertemplabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.watertemptestbuttonlayout)
        try:
            self.watertempbeginbutton = QPushButton("Begin", self)
            self.watertempbeginbutton.setFixedWidth(200)
            self.watertempbeginbutton.clicked.connect(self.WaterTemp)
            self.watertemptestbuttonlayout.addWidget(self.watertempbeginbutton,
                                                alignment=Qt.AlignmentFlag.AlignCenter)

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

        watertemp.setLayout(layout)
        self.tabs.addTab(watertemp, f"Water Temperature Supply")

        # ------------------------------------------------------- Lamp Test
        lamp = QWidget()

        self.lamp_passed = [False, False, False]
        self.lamp_failed = [False, False, False]
        self.lamp_completed = False
        self.current_lamp_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.lamptestbuttonlayout = QHBoxLayout()

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

        self.lamplabel = QLabel(
            "<b>Lamp Test step one. </b><br><br>"

            "<i> Lamp test step one condition </i><br><br>"
        )

        self.lamplabel.setTextFormat(Qt.TextFormat.RichText)
        self.lamplabel.setWordWrap(True)
        self.lamplabel.setStyleSheet("""
                                                    font-size: 18px;
                                                    padding-top: 50px;
                                                    padding-left: 50px;
                                                    padding-right: 50px;
                                                    padding-bottom: 50px;
                                                    """)
        self.lamplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.lamplabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.lamptestbuttonlayout)
        try:
            self.lampbeginbutton = QPushButton("Begin", self)
            self.lampbeginbutton.setFixedWidth(200)
            self.lampbeginbutton.clicked.connect(self.Lamp)
            self.lamptestbuttonlayout.addWidget(self.lampbeginbutton,
                                                     alignment=Qt.AlignmentFlag.AlignCenter)

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

        lamp.setLayout(layout)
        self.tabs.addTab(lamp, f"Lamp")

        # ------------------------------------------------------- Fill Test
        fill = QWidget()

        self.fill_passed = [False, False, False]
        self.fill_failed = [False, False, False]
        self.fill_completed = False
        self.current_fill_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.filltestbuttonlayout = QHBoxLayout()

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

        self.filllabel = QLabel(
            "<b>Fill Test step one. </b><br><br>"

            "<i> Fill test step one condition </i><br><br>"
        )

        self.filllabel.setTextFormat(Qt.TextFormat.RichText)
        self.filllabel.setWordWrap(True)
        self.filllabel.setStyleSheet("""
                                                            font-size: 18px;
                                                            padding-top: 50px;
                                                            padding-left: 50px;
                                                            padding-right: 50px;
                                                            padding-bottom: 50px;
                                                            """)
        self.filllabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.filllabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.filltestbuttonlayout)
        try:
            self.fillbeginbutton = QPushButton("Begin", self)
            self.fillbeginbutton.setFixedWidth(200)
            self.fillbeginbutton.clicked.connect(self.Fill)
            self.filltestbuttonlayout.addWidget(self.fillbeginbutton,
                                                alignment=Qt.AlignmentFlag.AlignCenter)

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

        fill.setLayout(layout)
        self.tabs.addTab(fill, f"Fill")

        # ------------------------------------------------------- Preheat Test
        preheat = QWidget()
        self.preheat_passed = [False, False, False]
        self.preheat_failed = [False, False, False]
        self.preheat_completed = False
        self.current_preheat_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.preheattestbuttonlayout = QHBoxLayout()

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

        self.preheatlabel = QLabel(
            "<b>Preheat Test step one. </b><br><br>"

            "<i> Preheat test step one condition </i><br><br>"
        )

        self.preheatlabel.setTextFormat(Qt.TextFormat.RichText)
        self.preheatlabel.setWordWrap(True)
        self.preheatlabel.setStyleSheet("""
                                                                    font-size: 18px;
                                                                    padding-top: 50px;
                                                                    padding-left: 50px;
                                                                    padding-right: 50px;
                                                                    padding-bottom: 50px;
                                                                    """)
        self.preheatlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.preheatlabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.preheattestbuttonlayout)
        try:
            self.preheatbeginbutton = QPushButton("Begin", self)
            self.preheatbeginbutton.setFixedWidth(200)
            self.preheatbeginbutton.clicked.connect(self.Preheat)
            self.preheattestbuttonlayout.addWidget(self.preheatbeginbutton,
                                                alignment=Qt.AlignmentFlag.AlignCenter)

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

        preheat.setLayout(layout)
        self.tabs.addTab(preheat, f"Preheat")

        # ------------------------------------------------------- Heater Test
        heater = QWidget()
        self.heater_passed = [False, False, False]
        self.heater_failed = [False, False, False]
        self.heater_completed = False
        self.current_heater_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.heatertestbuttonlayout = QHBoxLayout()

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

        self.heaterlabel = QLabel(
            "<b>Heater Test step one. </b><br><br>"

            "<i> Heater test step one condition </i><br><br>"
        )

        self.heaterlabel.setTextFormat(Qt.TextFormat.RichText)
        self.heaterlabel.setWordWrap(True)
        self.heaterlabel.setStyleSheet("""
                                                                            font-size: 18px;
                                                                            padding-top: 50px;
                                                                            padding-left: 50px;
                                                                            padding-right: 50px;
                                                                            padding-bottom: 50px;
                                                                            """)
        self.heaterlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.heaterlabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.heatertestbuttonlayout)
        try:
            self.heaterbeginbutton = QPushButton("Begin", self)
            self.heaterbeginbutton.setFixedWidth(200)
            self.heaterbeginbutton.clicked.connect(self.Heater)
            self.heatertestbuttonlayout.addWidget(self.heaterbeginbutton,
                                                   alignment=Qt.AlignmentFlag.AlignCenter)

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

        heater.setLayout(layout)
        self.tabs.addTab(heater, f"Heater")

        # ------------------------------------------------------- Tea Test
        tea = QWidget()
        self.tea_passed = [False, False, False]
        self.tea_failed = [False, False, False]
        self.tea_completed = False
        self.current_tea_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.teatestbuttonlayout = QHBoxLayout()

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

        self.tealabel = QLabel(
            "<b>Tea Test step one. </b><br><br>"

            "<i> Tea test step one condition </i><br><br>"
        )

        self.tealabel.setTextFormat(Qt.TextFormat.RichText)
        self.tealabel.setWordWrap(True)
        self.tealabel.setStyleSheet("""
                                                                                    font-size: 18px;
                                                                                    padding-top: 50px;
                                                                                    padding-left: 50px;
                                                                                    padding-right: 50px;
                                                                                    padding-bottom: 50px;
                                                                                    """)
        self.tealabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.tealabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.teatestbuttonlayout)
        try:
            self.teabeginbutton = QPushButton("Begin", self)
            self.teabeginbutton.setFixedWidth(200)
            self.teabeginbutton.clicked.connect(self.Tea)
            self.teatestbuttonlayout.addWidget(self.teabeginbutton,
                                                  alignment=Qt.AlignmentFlag.AlignCenter)

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

        tea.setLayout(layout)
        self.tabs.addTab(tea, f"Tea")

        # ------------------------------------------------------- Hot Plate Test
        hotplate = QWidget()
        self.hotplate_passed = [False, False, False]
        self.hotplate_failed = [False, False, False]
        self.hotplate_completed = False
        self.current_hotplate_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.hotplatetestbuttonlayout = QHBoxLayout()

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

        self.hotplatelabel = QLabel(
            "<b>Hotplate Test step one. </b><br><br>"

            "<i> Hotplate test step one condition </i><br><br>"
        )

        self.hotplatelabel.setTextFormat(Qt.TextFormat.RichText)
        self.hotplatelabel.setWordWrap(True)
        self.hotplatelabel.setStyleSheet("""
                                                                                            font-size: 18px;
                                                                                            padding-top: 50px;
                                                                                            padding-left: 50px;
                                                                                            padding-right: 50px;
                                                                                            padding-bottom: 50px;
                                                                                            """)
        self.hotplatelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.hotplatelabel)
        layout.addWidget(self.scroll)
        layout.addLayout(self.hotplatetestbuttonlayout)
        try:
            self.hotplatebeginbutton = QPushButton("Begin", self)
            self.hotplatebeginbutton.setFixedWidth(200)
            self.hotplatebeginbutton.clicked.connect(self.HotPlate)
            self.hotplatetestbuttonlayout.addWidget(self.hotplatebeginbutton,
                                               alignment=Qt.AlignmentFlag.AlignCenter)

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

        hotplate.setLayout(layout)
        self.tabs.addTab(hotplate, f"Hotplate")

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
        print("Restarting Resistance Test")

    def ResistanceResults(self):
        print("Printing Resistance Test Results")

    def Leak(self):
        try:
            leakmsg = QMessageBox()
            leakmsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_leak_step == 0:
                leakmsg.setWindowTitle("Leak test one")
                leakmsg.setText("Leak one condition")
                pass_button = leakmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = leakmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                leakmsg.exec()

                if leakmsg.clickedButton() == pass_button:
                    self.leak_passed[0] = True
                    self.leak_failed[0] = False
                    self.updateLeakStep()
                    self.current_leak_step += 1
                elif leakmsg.clickedButton() == fail_button:
                    self.leak_passed[0] = False
                    self.leak_failed[0] = True
                    self.updateLeakStep()
                    self.current_leak_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_leak_step == 1:
                leakmsg.setWindowTitle("Leak Step Two")
                leakmsg.setText("Leak step two condition")
                pass_button = leakmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = leakmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                leakmsg.exec()

                if leakmsg.clickedButton() == pass_button:
                    self.leak_passed[1] = True
                    self.leak_failed[1] = False
                    self.updateLeakStep()
                    self.current_leak_step += 1
                elif leakmsg.clickedButton() == fail_button:
                    self.leak_passed[1] = False
                    self.leak_failed[1] = True
                    self.updateLeakStep()
                    self.current_leak_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_leak_step == 2:
                leakmsg.setWindowTitle("Leak Step Three")
                leakmsg.setText("Leak step three condition")
                pass_button = leakmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = leakmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                leakmsg.exec()

                if leakmsg.clickedButton() == pass_button:
                    self.leak_passed[2] = True
                    self.leak_failed[2] = False
                    self.leak_completed = True
                    self.updateLeakStep()
                    self.current_leak_step += 1
                elif leakmsg.clickedButton() == fail_button:
                    self.leak_passed[2] = False
                    self.leak_failed[2] = True
                    self.updateLeakStep()
                    self.current_leak_step += 1

            # Completed
            elif self.leak_completed:
                leakmsg.setWindowTitle("Test Completed!")
                leakmsg.setText("The Leak test has been completed successfully.")
                leakmsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                leakmsg.exec()

                self.updateLeakStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateLeakStep(self):
        if self.leak_passed[0] or self.leak_failed[0]:

            self.leaklabel.setText(
                                "<b>Leak step two instructions</b><br><br>"
                                "<i>Leak step two conditions.</i><br><br>"
                               )

            self.leakbeginbutton.setText("Continue")
            self.leakbeginbutton.clicked.disconnect()
            self.leakbeginbutton.clicked.connect(self.Leak)

        if self.leak_passed[1] or self.leak_failed[1]:

            self.leaklabel.setText(
                                "<b>Leak Step Three.</b><br><br>"
                                "<i>Leak step three condition.</i><br><br>"
                                )

            self.leakbeginbutton.setText("Continue")
            self.leakbeginbutton.clicked.disconnect()
            self.leakbeginbutton.clicked.connect(self.Leak)

        if self.leak_passed[2] or self.leak_failed[2]:
            self.leaklabel.setText(
                                         "<b>Leak Test Completed!</b><br><br>"
                                         "<b>Leak test closing step.<br><br>"
                                        )
            self.leakbeginbutton.setText("Results")
            self.leakbeginbutton.clicked.disconnect()
            self.leakbeginbutton.clicked.connect(self.LeakResults)

            self.leakrestart = QPushButton("Restart", self)
            self.leakrestart.clicked.connect(self.LeakRestart)
            self.leakrestart.setFixedWidth(200)
            self.leaktestbuttonlayout.addWidget(self.leakrestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def LeakRestart(self):
        print("Restarting Leak Test")

    def LeakResults(self):
        print("Printing Leak Test Results")

    def WaterTemp(self):
        try:
            watertempmsg = QMessageBox()
            watertempmsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_watertemp_step == 0:
                watertempmsg.setWindowTitle("Water Supply Temperature test one")
                watertempmsg.setText("Water Supply Temperature one condition")
                pass_button = watertempmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = watertempmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                watertempmsg.exec()

                if watertempmsg.clickedButton() == pass_button:
                    self.watertemp_passed[0] = True
                    self.watertemp_failed[0] = False
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1
                elif watertempmsg.clickedButton() == fail_button:
                    self.watertemp_passed[0] = False
                    self.watertemp_failed[0] = True
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_watertemp_step == 1:
                watertempmsg.setWindowTitle("Leak Step Two")
                watertempmsg.setText("Leak step two condition")
                pass_button = watertempmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = watertempmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                watertempmsg.exec()

                if watertempmsg.clickedButton() == pass_button:
                    self.watertemp_passed[1] = True
                    self.watertemp_failed[1] = False
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1
                elif watertempmsg.clickedButton() == fail_button:
                    self.watertemp_passed[1] = False
                    self.watertemp_failed[1] = True
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_watertemp_step == 2:
                watertempmsg.setWindowTitle("Water Supply Temperature Step Three")
                watertempmsg.setText("Water supply temperature step three condition")
                pass_button = watertempmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = watertempmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                watertempmsg.exec()

                if watertempmsg.clickedButton() == pass_button:
                    self.watertemp_passed[2] = True
                    self.watertemp_failed[2] = False
                    self.watertemp_completed = True
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1
                elif watertempmsg.clickedButton() == fail_button:
                    self.watertemp_passed[2] = False
                    self.watertemp_failed[2] = True
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1

            # Completed
            elif self.watertemp_completed:
                watertempmsg.setWindowTitle("Test Completed!")
                watertempmsg.setText("The Water Supply Temperature test has been completed successfully.")
                watertempmsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                watertempmsg.exec()

                self.updateWaterTempStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateWaterTempStep(self):
        if self.watertemp_passed[0] or self.watertemp_failed[0]:

            self.watertemplabel.setText(
                                "<b>Water Supply Temperature step two instructions</b><br><br>"
                                "<i>Water supply temperature step two conditions.</i><br><br>"
                               )

            self.watertempbeginbutton.setText("Continue")
            self.watertempbeginbutton.clicked.disconnect()
            self.watertempbeginbutton.clicked.connect(self.WaterTemp)

        if self.watertemp_passed[1] or self.watertemp_failed[1]:

            self.watertemplabel.setText(
                                "<b>Water Supply Temperature Step Three.</b><br><br>"
                                "<i>Water supply temperature step three condition.</i><br><br>"
                                )

            self.watertempbeginbutton.setText("Continue")
            self.watertempbeginbutton.clicked.disconnect()
            self.watertempbeginbutton.clicked.connect(self.WaterTemp)

        if self.watertemp_passed[2] or self.watertemp_failed[2]:
            self.watertemplabel.setText(
                                         "<b>Water Supply Temperature Test Completed!</b><br><br>"
                                         "<b>Water supply temperature test closing step.<br><br>"
                                        )
            self.watertempbeginbutton.setText("Results")
            self.watertempbeginbutton.clicked.disconnect()
            self.watertempbeginbutton.clicked.connect(self.WaterTempResults)

            self.watertemprestart = QPushButton("Restart", self)
            self.watertemprestart.clicked.connect(self.WaterTempRestart)
            self.watertemprestart.setFixedWidth(200)
            self.watertemptestbuttonlayout.addWidget(self.watertemprestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def WaterTempRestart(self):
        print("Restarting Water Supply Temperature Test")

    def WaterTempResults(self):
        print("Printing Water Supply Temperature Test Results")


    def Lamp(self):
        try:
            lampmsg = QMessageBox()
            lampmsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_lamp_step == 0:
                lampmsg.setWindowTitle("Lamp test one")
                lampmsg.setText("Lamp test one condition")
                pass_button = lampmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = lampmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                lampmsg.exec()

                if lampmsg.clickedButton() == pass_button:
                    self.lamp_passed[0] = True
                    self.lamp_failed[0] = False
                    self.updateLampStep()
                    self.current_lamp_step += 1
                elif lampmsg.clickedButton() == fail_button:
                    self.lamp_passed[0] = False
                    self.lamp_failed[0] = True
                    self.updateLampStep()
                    self.current_lamp_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_lamp_step == 1:
                lampmsg.setWindowTitle("Lamp Step Two")
                lampmsg.setText("Lamp step two condition")
                pass_button = lampmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = lampmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                lampmsg.exec()

                if lampmsg.clickedButton() == pass_button:
                    self.lamp_passed[1] = True
                    self.lamp_failed[1] = False
                    self.updateLampStep()
                    self.current_lamp_step += 1
                elif lampmsg.clickedButton() == fail_button:
                    self.lamp_passed[1] = False
                    self.lamp_failed[1] = True
                    self.updateLampStep()
                    self.current_lamp_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_lamp_step == 2:
                lampmsg.setWindowTitle("Lamp Test Step Three")
                lampmsg.setText("Lamp test step three condition")
                pass_button = lampmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = lampmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                lampmsg.exec()

                if lampmsg.clickedButton() == pass_button:
                    self.lamp_passed[2] = True
                    self.lamp_failed[2] = False
                    self.lamp_completed = True
                    self.updateLampStep()
                    self.current_lamp_step += 1
                elif lampmsg.clickedButton() == fail_button:
                    self.lamp_passed[2] = False
                    self.lamp_failed[2] = True
                    self.updateLampStep()
                    self.current_lamp_step += 1

            # Completed
            elif self.lamp_completed:
                lampmsg.setWindowTitle("Test Completed!")
                lampmsg.setText("The Lamp test has been completed successfully.")
                lampmsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                lampmsg.exec()

                self.updateLampStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateLampStep(self):
        if self.lamp_passed[0] or self.lamp_failed[0]:

            self.lamplabel.setText(
                                "<b>Lamp test step two instructions</b><br><br>"
                                "<i>Lamp test step two conditions.</i><br><br>"
                               )

            self.lampbeginbutton.setText("Continue")
            self.lampbeginbutton.clicked.disconnect()
            self.lampbeginbutton.clicked.connect(self.Lamp)

        if self.lamp_passed[1] or self.lamp_failed[1]:

            self.lamplabel.setText(
                                "<b>Lamp Test Step Three.</b><br><br>"
                                "<i>Lamp test step three condition.</i><br><br>"
                                )

            self.lampbeginbutton.setText("Continue")
            self.lampbeginbutton.clicked.disconnect()
            self.lampbeginbutton.clicked.connect(self.Lamp)

        if self.lamp_passed[2] or self.lamp_failed[2]:
            self.lamplabel.setText(
                                         "<b>Lamp Test Completed!</b><br><br>"
                                         "<b>Lamp test closing step.<br><br>"
                                        )
            self.lampbeginbutton.setText("Results")
            self.lampbeginbutton.clicked.disconnect()
            self.lampbeginbutton.clicked.connect(self.LampResults)

            self.lamprestart = QPushButton("Restart", self)
            self.lamprestart.clicked.connect(self.LampRestart)
            self.lamprestart.setFixedWidth(200)
            self.lamptestbuttonlayout.addWidget(self.lamprestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def LampRestart(self):
        print("Restarting Lamp Test")

    def LampResults(self):
        print("Printing Lamp Test Results")

    def Fill(self):
        try:
            fillmsg = QMessageBox()
            fillmsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_fill_step == 0:
                fillmsg.setWindowTitle("Fill test one")
                fillmsg.setText("Fill test one condition")
                pass_button = fillmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = fillmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                fillmsg.exec()

                if fillmsg.clickedButton() == pass_button:
                    self.fill_passed[0] = True
                    self.fill_failed[0] = False
                    self.updateFillStep()
                    self.current_fill_step += 1
                elif fillmsg.clickedButton() == fail_button:
                    self.fill_passed[0] = False
                    self.fill_failed[0] = True
                    self.updateFillStep()
                    self.current_fill_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_fill_step == 1:
                fillmsg.setWindowTitle("Fill Test Step Two")
                fillmsg.setText("Fill test step two condition")
                pass_button = fillmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = fillmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                fillmsg.exec()

                if fillmsg.clickedButton() == pass_button:
                    self.fill_passed[1] = True
                    self.fill_failed[1] = False
                    self.updateFillStep()
                    self.current_fill_step += 1
                elif fillmsg.clickedButton() == fail_button:
                    self.fill_passed[1] = False
                    self.fill_failed[1] = True
                    self.updateFillStep()
                    self.current_fill_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_fill_step == 2:
                fillmsg.setWindowTitle("Fill Test Step Three")
                fillmsg.setText("Fill test step three condition")
                pass_button = fillmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = fillmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                fillmsg.exec()

                if fillmsg.clickedButton() == pass_button:
                    self.fill_passed[2] = True
                    self.fill_failed[2] = False
                    self.fill_completed = True
                    self.updateFillStep()
                    self.current_fill_step += 1
                elif fillmsg.clickedButton() == fail_button:
                    self.fill_passed[2] = False
                    self.fill_failed[2] = True
                    self.updateFillStep()
                    self.current_fill_step += 1

            # Completed
            elif self.fill_completed:
                fillmsg.setWindowTitle("Test Completed!")
                fillmsg.setText("The Fill test has been completed successfully.")
                fillmsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                fillmsg.exec()

                self.updateFillStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateFillStep(self):
        if self.fill_passed[0] or self.fill_failed[0]:

            self.filllabel.setText(
                                "<b>Fill test step two instructions</b><br><br>"
                                "<i>Fill test step two conditions.</i><br><br>"
                               )

            self.fillbeginbutton.setText("Continue")
            self.fillbeginbutton.clicked.disconnect()
            self.fillbeginbutton.clicked.connect(self.Fill)

        if self.fill_passed[1] or self.fill_failed[1]:

            self.filllabel.setText(
                                "<b>Fill Test Step Three.</b><br><br>"
                                "<i>Fill test step three condition.</i><br><br>"
                                )

            self.fillbeginbutton.setText("Continue")
            self.fillbeginbutton.clicked.disconnect()
            self.fillbeginbutton.clicked.connect(self.Fill)

        if self.fill_passed[2] or self.fill_failed[2]:
            self.filllabel.setText(
                                         "<b>Fill Test Completed!</b><br><br>"
                                         "<b>Fill test closing step.<br><br>"
                                        )
            self.fillbeginbutton.setText("Results")
            self.fillbeginbutton.clicked.disconnect()
            self.fillbeginbutton.clicked.connect(self.FillResults)

            self.fillrestart = QPushButton("Restart", self)
            self.fillrestart.clicked.connect(self.FillRestart)
            self.fillrestart.setFixedWidth(200)
            self.filltestbuttonlayout.addWidget(self.fillrestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def FillRestart(self):
        print("Restarting Fill Test")

    def FillResults(self):
        print("Printing Fill Test Results")


    def Preheat(self):
        try:
            preheatmsg = QMessageBox()
            preheatmsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_preheat_step == 0:
                preheatmsg.setWindowTitle("Preheat test one")
                preheatmsg.setText("Preheat test one condition")
                pass_button = preheatmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = preheatmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                preheatmsg.exec()

                if preheatmsg.clickedButton() == pass_button:
                    self.preheat_passed[0] = True
                    self.preheat_failed[0] = False
                    self.updatePreheatStep()
                    self.current_preheat_step += 1
                elif preheatmsg.clickedButton() == fail_button:
                    self.preheat_passed[0] = False
                    self.preheat_failed[0] = True
                    self.updatePreheatStep()
                    self.current_preheat_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_preheat_step == 1:
                preheatmsg.setWindowTitle("Preheat Test Step Two")
                preheatmsg.setText("Preheat test step two condition")
                pass_button = preheatmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = preheatmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                preheatmsg.exec()

                if preheatmsg.clickedButton() == pass_button:
                    self.preheat_passed[1] = True
                    self.preheat_failed[1] = False
                    self.updatePreheatStep()
                    self.current_preheat_step += 1
                elif preheatmsg.clickedButton() == fail_button:
                    self.preheat_passed[1] = False
                    self.preheat_failed[1] = True
                    self.updatePreheatStep()
                    self.current_preheat_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_preheat_step == 2:
                preheatmsg.setWindowTitle("Preheat Test Step Three")
                preheatmsg.setText("Preheat test step three condition")
                pass_button = preheatmsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = preheatmsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                preheatmsg.exec()

                if preheatmsg.clickedButton() == pass_button:
                    self.preheat_passed[2] = True
                    self.preheat_failed[2] = False
                    self.preheat_completed = True
                    self.updatePreheatStep()
                    self.current_preheat_step += 1
                elif preheatmsg.clickedButton() == fail_button:
                    self.preheat_passed[2] = False
                    self.preheat_failed[2] = True
                    self.updatePreheatStep()
                    self.current_preheat_step += 1

            # Completed
            elif self.preheat_completed:
                preheatmsg.setWindowTitle("Test Completed!")
                preheatmsg.setText("The Preheat test has been completed successfully.")
                preheatmsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                preheatmsg.exec()

                self.updatePreheatStep()

        except Exception as e:
            print(f"Error: {e}")

    def updatePreheatStep(self):
        if self.preheat_passed[0] or self.preheat_failed[0]:

            self.preheatlabel.setText(
                                "<b>Preheat test step two instructions</b><br><br>"
                                "<i>Preheat test step two conditions.</i><br><br>"
                               )

            self.preheatbeginbutton.setText("Continue")
            self.preheatbeginbutton.clicked.disconnect()
            self.preheatbeginbutton.clicked.connect(self.Preheat)

        if self.preheat_passed[1] or self.preheat_failed[1]:

            self.preheatlabel.setText(
                                "<b>Preheat Test Step Three.</b><br><br>"
                                "<i>Preheat test step three condition.</i><br><br>"
                                )

            self.preheatbeginbutton.setText("Continue")
            self.preheatbeginbutton.clicked.disconnect()
            self.preheatbeginbutton.clicked.connect(self.Preheat)

        if self.preheat_passed[2] or self.preheat_failed[2]:
            self.preheatlabel.setText(
                                         "<b>Preheat Test Completed!</b><br><br>"
                                         "<b>Preheat test closing step.<br><br>"
                                        )
            self.preheatbeginbutton.setText("Results")
            self.preheatbeginbutton.clicked.disconnect()
            self.preheatbeginbutton.clicked.connect(self.PreheatResults)

            self.preheatrestart = QPushButton("Restart", self)
            self.preheatrestart.clicked.connect(self.PreheatRestart)
            self.preheatrestart.setFixedWidth(200)
            self.preheattestbuttonlayout.addWidget(self.preheatrestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def PreheatRestart(self):
        print("Restarting Preheat Test")

    def PreheatResults(self):
        print("Printing Preheat Test Results")


    def Heater(self):
        try:
            heatermsg = QMessageBox()
            heatermsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_heater_step == 0:
                heatermsg.setWindowTitle("Heater test one")
                heatermsg.setText("Heater test one condition")
                pass_button = heatermsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = heatermsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                heatermsg.exec()

                if heatermsg.clickedButton() == pass_button:
                    self.heater_passed[0] = True
                    self.heater_failed[0] = False
                    self.updateHeaterStep()
                    self.current_heater_step += 1
                elif heatermsg.clickedButton() == fail_button:
                    self.heater_passed[0] = False
                    self.heater_failed[0] = True
                    self.updateHeaterStep()
                    self.current_heater_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_heater_step == 1:
                heatermsg.setWindowTitle("Heater Test Step Two")
                heatermsg.setText("Heater test step two condition")
                pass_button = heatermsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = heatermsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                heatermsg.exec()

                if heatermsg.clickedButton() == pass_button:
                    self.heater_passed[1] = True
                    self.heater_failed[1] = False
                    self.updateHeaterStep()
                    self.current_heater_step += 1
                elif heatermsg.clickedButton() == fail_button:
                    self.heater_passed[1] = False
                    self.heater_failed[1] = True
                    self.updateHeaterStep()
                    self.current_heater_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_heater_step == 2:
                heatermsg.setWindowTitle("Heater Test Step Three")
                heatermsg.setText("Heater test step three condition")
                pass_button = heatermsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = heatermsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                heatermsg.exec()

                if heatermsg.clickedButton() == pass_button:
                    self.heater_passed[2] = True
                    self.heater_failed[2] = False
                    self.heater_completed = True
                    self.updateHeaterStep()
                    self.current_heater_step += 1
                elif heatermsg.clickedButton() == fail_button:
                    self.heater_passed[2] = False
                    self.heater_failed[2] = True
                    self.updateHeaterStep()
                    self.current_heater_step += 1

            # Completed
            elif self.heater_completed:
                heatermsg.setWindowTitle("Test Completed!")
                heatermsg.setText("The Heater test has been completed successfully.")
                heatermsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                heatermsg.exec()

                self.updateHeaterStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHeaterStep(self):
        if self.heater_passed[0] or self.heater_failed[0]:

            self.heaterlabel.setText(
                                "<b>Heater test step two instructions</b><br><br>"
                                "<i>Heater test step two conditions.</i><br><br>"
                               )

            self.heaterbeginbutton.setText("Continue")
            self.heaterbeginbutton.clicked.disconnect()
            self.heaterbeginbutton.clicked.connect(self.Heater)

        if self.heater_passed[1] or self.heater_failed[1]:

            self.heaterlabel.setText(
                                "<b>Heater Test Step Three.</b><br><br>"
                                "<i>Heater test step three condition.</i><br><br>"
                                )

            self.heaterbeginbutton.setText("Continue")
            self.heaterbeginbutton.clicked.disconnect()
            self.heaterbeginbutton.clicked.connect(self.Heater)

        if self.heater_passed[2] or self.heater_failed[2]:
            self.heaterlabel.setText(
                                         "<b>Heater Test Completed!</b><br><br>"
                                         "<b>Heater test closing step.<br><br>"
                                        )
            self.heaterbeginbutton.setText("Results")
            self.heaterbeginbutton.clicked.disconnect()
            self.heaterbeginbutton.clicked.connect(self.HeaterResults)

            self.heaterrestart = QPushButton("Restart", self)
            self.heaterrestart.clicked.connect(self.HeaterRestart)
            self.heaterrestart.setFixedWidth(200)
            self.heatertestbuttonlayout.addWidget(self.heaterrestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def HeaterRestart(self):
        print("Restarting Heater Test")

    def HeaterResults(self):
        print("Printing Heater Test Results")


    def Tea(self):
        try:
            teamsg = QMessageBox()
            teamsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_tea_step == 0:
                teamsg.setWindowTitle("Tea test one")
                teamsg.setText("Tea test one condition")
                pass_button = teamsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = teamsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                teamsg.exec()

                if teamsg.clickedButton() == pass_button:
                    self.tea_passed[0] = True
                    self.tea_failed[0] = False
                    self.updateTeaStep()
                    self.current_tea_step += 1
                elif teamsg.clickedButton() == fail_button:
                    self.tea_passed[0] = False
                    self.tea_failed[0] = True
                    self.updateTeaStep()
                    self.current_tea_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_tea_step == 1:
                teamsg.setWindowTitle("Tea Test Step Two")
                teamsg.setText("Tea test step two condition")
                pass_button = teamsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = teamsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                teamsg.exec()

                if teamsg.clickedButton() == pass_button:
                    self.tea_passed[1] = True
                    self.tea_failed[1] = False
                    self.updateTeaStep()
                    self.current_tea_step += 1
                elif teamsg.clickedButton() == fail_button:
                    self.tea_passed[1] = False
                    self.tea_failed[1] = True
                    self.updateTeaStep()
                    self.current_tea_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_tea_step == 2:
                teamsg.setWindowTitle("Tea Test Step Three")
                teamsg.setText("Tea test step three condition")
                pass_button = teamsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = teamsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                teamsg.exec()

                if teamsg.clickedButton() == pass_button:
                    self.tea_passed[2] = True
                    self.tea_failed[2] = False
                    self.tea_completed = True
                    self.updateTeaStep()
                    self.current_tea_step += 1
                elif teamsg.clickedButton() == fail_button:
                    self.tea_passed[2] = False
                    self.tea_failed[2] = True
                    self.updateTeaStep()
                    self.current_tea_step += 1

            # Completed
            elif self.tea_completed:
                teamsg.setWindowTitle("Test Completed!")
                teamsg.setText("The Tea test has been completed successfully.")
                teamsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                teamsg.exec()

                self.updateTeaStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateTeaStep(self):
        if self.tea_passed[0] or self.tea_failed[0]:

            self.tealabel.setText(
                                "<b>Tea test step two instructions</b><br><br>"
                                "<i>Tea test step two conditions.</i><br><br>"
                               )

            self.teabeginbutton.setText("Continue")
            self.teabeginbutton.clicked.disconnect()
            self.teabeginbutton.clicked.connect(self.Tea)

        if self.tea_passed[1] or self.tea_failed[1]:

            self.tealabel.setText(
                                "<b>Tea Test Step Three.</b><br><br>"
                                "<i>Tea test step three condition.</i><br><br>"
                                )

            self.teabeginbutton.setText("Continue")
            self.teabeginbutton.clicked.disconnect()
            self.teabeginbutton.clicked.connect(self.Tea)

        if self.tea_passed[2] or self.tea_failed[2]:
            self.tealabel.setText(
                                         "<b>Tea Test Completed!</b><br><br>"
                                         "<b>Tea test closing step.<br><br>"
                                        )
            self.teabeginbutton.setText("Results")
            self.teabeginbutton.clicked.disconnect()
            self.teabeginbutton.clicked.connect(self.TeaResults)

            self.tearestart = QPushButton("Restart", self)
            self.tearestart.clicked.connect(self.TeaRestart)
            self.tearestart.setFixedWidth(200)
            self.teatestbuttonlayout.addWidget(self.tearestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def TeaRestart(self):
        print("Restarting Tea Test")

    def TeaResults(self):
        print("Printing Tea Test Results")


    def HotPlate(self):
        try:
            hotplatemsg = QMessageBox()
            hotplatemsg.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_hotplate_step == 0:
                hotplatemsg.setWindowTitle("Hot Plate test one")
                hotplatemsg.setText("Hot Plate test one condition")
                pass_button = hotplatemsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = hotplatemsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                hotplatemsg.exec()

                if hotplatemsg.clickedButton() == pass_button:
                    self.hotplate_passed[0] = True
                    self.hotplate_failed[0] = False
                    self.updateHotPlateStep()
                    self.current_hotplate_step += 1
                elif hotplatemsg.clickedButton() == fail_button:
                    self.hotplate_passed[0] = False
                    self.hotplate_failed[0] = True
                    self.updateHotPlateStep()
                    self.current_hotplate_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_hotplate_step == 1:
                hotplatemsg.setWindowTitle("Hot Plate Test Step Two")
                hotplatemsg.setText("Hot Plate step two condition")
                pass_button = hotplatemsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = hotplatemsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                hotplatemsg.exec()

                if hotplatemsg.clickedButton() == pass_button:
                    self.hotplate_passed[1] = True
                    self.hotplate_failed[1] = False
                    self.updateHotPlateStep()
                    self.current_hotplate_step += 1
                elif hotplatemsg.clickedButton() == fail_button:
                    self.hotplate_passed[1] = False
                    self.hotplate_failed[1] = True
                    self.updateHotPlateStep()
                    self.current_hotplate_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_hotplate_step == 2:
                hotplatemsg.setWindowTitle("Hot Plate Test Step Three")
                hotplatemsg.setText("Hot Plate test step three condition")
                pass_button = hotplatemsg.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = hotplatemsg.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                hotplatemsg.exec()

                if hotplatemsg.clickedButton() == pass_button:
                    self.hotplate_passed[2] = True
                    self.hotplate_failed[2] = False
                    self.hotplate_completed = True
                    self.updateHotPlateStep()
                    self.current_hotplate_step += 1
                elif hotplatemsg.clickedButton() == fail_button:
                    self.hotplate_passed[2] = False
                    self.hotplate_failed[2] = True
                    self.updateHotPlateStep()
                    self.current_hotplate_step += 1

            # Completed
            elif self.hotplate_completed:
                hotplatemsg.setWindowTitle("Test Completed!")
                hotplatemsg.setText("The Hot Plate test has been completed successfully.")
                hotplatemsg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                hotplatemsg.exec()

                self.updateHotPlateStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHotPlateStep(self):
        if self.hotplate_passed[0] or self.hotplate_failed[0]:

            self.hotplatelabel.setText(
                                "<b>Hot Plate test step two instructions</b><br><br>"
                                "<i>Hot Plate test step two conditions.</i><br><br>"
                               )

            self.hotplatebeginbutton.setText("Continue")
            self.hotplatebeginbutton.clicked.disconnect()
            self.hotplatebeginbutton.clicked.connect(self.HotPlate)

        if self.hotplate_passed[1] or self.hotplate_failed[1]:

            self.hotplatelabel.setText(
                                "<b>Hot Plate Test Step Three.</b><br><br>"
                                "<i>Hot Plate test step three condition.</i><br><br>"
                                )

            self.hotplatebeginbutton.setText("Continue")
            self.hotplatebeginbutton.clicked.disconnect()
            self.hotplatebeginbutton.clicked.connect(self.HotPlate)

        if self.hotplate_passed[2] or self.hotplate_failed[2]:
            self.hotplatelabel.setText(
                                         "<b>Hot Plate Test Completed!</b><br><br>"
                                         "<b>Hot Plate test closing step.<br><br>"
                                        )
            self.hotplatebeginbutton.setText("Results")
            self.hotplatebeginbutton.clicked.disconnect()
            self.hotplatebeginbutton.clicked.connect(self.HotPlateResults)

            self.hotplaterestart = QPushButton("Restart", self)
            self.hotplaterestart.clicked.connect(self.HotPlateRestart)
            self.hotplaterestart.setFixedWidth(200)
            self.hotplatetestbuttonlayout.addWidget(self.hotplaterestart, alignment=Qt.AlignmentFlag.AlignCenter)



    def HotPlateRestart(self):
        print("Restarting Hot Plate Test")

    def HotPlateResults(self):
        print("Printing Hot Plate Test Results")






# === Application entry point ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

