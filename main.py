import sys
import os

from PyQt6.QtGui import QPixmap, QFontDatabase, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLineEdit, QComboBox, QSpacerItem
)

from PyQt6.QtWidgets import QTabBar
from PyQt6.QtCore import QSize, QThread, QTimer

from PyQt6.QtCore import Qt, pyqtSignal, QObject
#from PyQt6.QtWidgets.QWidget import setWindowFlag

from InstrumentWorker import InstrumentWorker

from Dielectric import DielectricTest
from HeatedWater import HeatedWaterTest
from PowerInterrupt import PowerInterruptTest
from Resistance import ResistanceTest
from AmbientTemp import AmbientTemperatureTest
from UnheatedWater import UnheatedWaterTest
from WaterSupplyTemperature import WaterTempTest
from TankPressure import TankPressureTest
from ServerRetainer import ServerRetainerTest
from Brew import BrewTest
from HeaterAndPreheater import HeaterAndPreheaterTest
from RTDCircuit import RTDCircuitTest
from PowerAndLowLight import PowerAndLowLightTest
from Tea import TeaTest
from VisualInspection import VisualInspectionTest
from LowWater import LowWaterTest
from WaterLeaks import WaterLeaksTest
from HeaterCurrent import HeaterCurrentTest
from HotWaterLight import HotWaterLightTest
from BrewBE import BrewBETest
from Temperature import TemperatureTest
from HeatedWater import HeatedWaterTest
from UnheatedWater import UnheatedWaterTest
from Lamp import LampTest
from HotPlate import HotPlateTest
from PowerInterrupt import PowerInterruptTest
from BrewInterrupt import BrewInterruptTest
from IREDMonitor import IREDMonitorTest
from PressureReliefValve import PressureReliefValveTest


import pyvisa

'''
rm = pyvisa.ResourceManager()
print(rm.list_resources())
my_instrument = rm.open_resource('GPIB0::3::INSTR')
print(my_instrument.write('COUP DIRECT'))
print(my_instrument.write('CURR:LIM 9.0'))
print(my_instrument.write('PROT:STAT 1'))
print(my_instrument.write('CURR:PROT:LEV 9.1'))



print(my_instrument.write('OUTP 1'))
print(my_instrument.write('VOLT 115'))
print(my_instrument.write('FREQ 400'))
print(my_instrument.query('OUTP?'))
'''
"""
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
"""

# === Main application window ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme = "Default"
        self.setWindowTitle("COMATS")
        #self.setFixedSize(800, 600)
        #self.theme = "Themes/MinimalBlue.qss"

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self.welcome = QWidget()
        self.setCentralWidget(self.welcome)
        #self.showFullScreen()

        self.welcomeLayout = QVBoxLayout()

        logoimage = "InAir"

        self.Logo = QPixmap(f"Images/{logoimage}.png")
        self.logoLabel = QLabel()
        #self.logoLabel.setStyleSheet("""
         #           padding-top: 0px;
          #          padding-bottom: 20px;
           #         padding-left: 100px;
            #        padding-right: 100px;
             #           """)
        #self.logoLabel.setScaledContents(True)
        self.logoLabel.setPixmap(self.Logo)
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logoLabel.setContentsMargins(100, 0, 100, 40)
        self.welcomeLayout.addWidget(self.logoLabel)


        self.welcomeLabel = QLabel("Welcome to COMATS")
        self.welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcomeLabel.setContentsMargins(100, 0, 100, 40)
        #self.welcomeLabel.setStyleSheet("""
         #                   padding-top: 50px;
          #                  padding-bottom: 50px;
           #                 padding-left: 100px;
            #                padding-right: 100px;
             #                   """)
        self.welcomeLayout.addWidget(self.welcomeLabel)
        self.welcomeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.welcome.setLayout(self.welcomeLayout)


        # Temporary Globals:

        global phase1read
        global phase2read
        global phase3read

        self.inst_thread = QThread(self)
        self.inst_worker = InstrumentWorker("GPIB0::3::INSTR", poll_ms=200)
        self.inst_worker.moveToThread(self.inst_thread)

        # lifecycle
        self.inst_thread.started.connect(self.inst_worker.start)
        self.inst_worker.finished.connect(self.inst_thread.quit)
        self.inst_worker.finished.connect(self.inst_worker.deleteLater)
        self.inst_thread.finished.connect(self.inst_thread.deleteLater)
        self.inst_thread.start()


        # when app quits, close instrument
        QApplication.instance().aboutToQuit.connect(self.inst_worker.shutdown)

        # --- Build tabs, pass the worker reference ---


        self.createNewWorkorder = False
        self.editExistingWorkorder = False
        self.runIndividualTests = False
        self.runAllTests = False


        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)



        self.createworkorder = QPushButton("Create New Workorder")
        self.createworkorder.setFixedWidth(200)
        self.createworkorder.clicked.connect(self.CreateNewWorkorder)
        self.buttonLayout.addWidget(self.createworkorder)

        self.openworkorder = QPushButton("Open Existing Workorder")
        self.openworkorder.setFixedWidth(200)
        self.openworkorder.clicked.connect(self.OpenExistingWorkorder)
        self.buttonLayout.addWidget(self.openworkorder)

        self.footerLayout = QHBoxLayout()

        self.settings = QPushButton("Settings")
        self.settings.setProperty("class", "small")
        #self.settings.setFixedWidth(10)
        self.settings.setFixedHeight(30)
        self.settings.clicked.connect(self.Settings)
        self.footerLayout.addWidget(self.settings, alignment=Qt.AlignmentFlag.AlignLeft)



        self.close = QPushButton("Exit")
        self.close.setProperty("class", "small")
        self.close.setFixedHeight(30)
        self.close.clicked.connect(self.CloseWindow)
        self.footerLayout.addWidget(self.close, alignment=Qt.AlignmentFlag.AlignCenter)

        self.version = QLabel("V. 2.0.1")
        self.version.setStyleSheet("""
                            font-size:12px;
                            """)
        self.version.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.footerLayout.addWidget(self.version)




        self.welcomeLayout.addLayout(self.buttonLayout)

        self.welcomeLayout.addSpacing(100)

        self.welcomeLayout.addLayout(self.footerLayout)




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
            self.setMinimumSize(400, 200)

            self.workorderentry = QWidget()
            self.setCentralWidget(self.workorderentry)

            layout = QVBoxLayout()

            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)



            woentrylayout = QVBoxLayout()
            woentrylayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            woentrylayout.setSpacing(5)

            woformlayout = QHBoxLayout()
            woformlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            woformlayout.setContentsMargins(0, 0, 0, 40)
            woformcontainer = QHBoxLayout()
            woformcontainer.addStretch(1)
            woformcontainer.addLayout(woformlayout)
            woformcontainer.addStretch(1)

            woentrylayout.addLayout(woformcontainer)

            wopromptlayout = QVBoxLayout()
            wopromptlayout.setSpacing(15)
            wopromptlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wopromptlayout.setContentsMargins(20, 0, 20, 0)

            wofieldlayout = QVBoxLayout()
            wofieldlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            #wofieldlayout.setContentsMargins(20, 0, 20, 0)

            """
            woseriallayout = QHBoxLayout()
            woseriallayout.setContentsMargins(20, 0, 20, 0)

            wopartnumberlayout = QHBoxLayout()
            wopartnumberlayout.setContentsMargins(20, 0, 20, 0)

            techlayout = QHBoxLayout()
            techlayout.setContentsMargins(20, 0, 20, 40)
            """

            wobuttonlayout = QVBoxLayout()
            wobuttonlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wobuttonlayout.setContentsMargins(20, 0, 20, 0)


            self.workordernumber = QLabel("Workorder Number: ")
            wopromptlayout.addWidget(self.workordernumber)

            self.workordernumberfield = QLineEdit()
            self.workordernumberfield.setMinimumWidth(300)
            self.workordernumberfield.setStyleSheet("""
                            QLineEdit {
                                border: none;
                                border-bottom: none;
                                outline: none;
                            }
                        """)
            self.workordernumberfield.setPlaceholderText("Enter workorder number...")
            wofieldlayout.addWidget(self.workordernumberfield)

            #woentrylayout.addLayout(wonumberlayout)

            self.workordermodel = QLabel("Unit Model Number: ")
            wopromptlayout.addWidget(self.workordermodel)

            self.workordermodelfield = QComboBox()
            self.workordermodelfield.setStyleSheet("""
                            QLineEdit {
                                border: none;
                                border-bottom: none;
                                outline: none;
                            }
                        """)
            self.workordermodelfield.addItem("11225-1")
            self.workordermodelfield.addItem("4810-28UG-00")
            wofieldlayout.addWidget(self.workordermodelfield)

            #woentrylayout.addLayout(womodellayout)



            self.serialnumber = QLabel("Unit Serial Number:  ")
            wopromptlayout.addWidget(self.serialnumber)

            self.serialnumberfield = QLineEdit()
            self.serialnumberfield.setStyleSheet("""
                QLineEdit {
                    border: none;
                    border-bottom: none;
                    outline: none;
                }
            """)
            self.serialnumberfield.setPlaceholderText("Enter serial number...")
            wofieldlayout.addWidget(self.serialnumberfield)

            #woentrylayout.addLayout(woseriallayout)

            self.unitpartnumber = QLabel("Unit Part Number:     ")
            wopromptlayout.addWidget(self.unitpartnumber)

            self.unitpartnumberfield = QLineEdit()
            self.unitpartnumberfield.setStyleSheet("""
                            QLineEdit {
                                border: none;
                                border-bottom: none;
                                outline: none;
                            }
                        """)
            self.unitpartnumberfield.setPlaceholderText("Enter part number...")
            wofieldlayout.addWidget(self.unitpartnumberfield)

            #woentrylayout.addLayout(wopartnumberlayout)

            self.tech = QLabel("Technician:                 ")
            wopromptlayout.addWidget(self.tech)

            self.techfield = QComboBox()
            self.techfield.setStyleSheet("""
                            QLineEdit {
                                border: none;
                                border-bottom: none;
                                outline: none;
                            }
                        """)
            self.techfield.addItem("Carlos")
            self.techfield.addItem("Brad")
            self.techfield.addItem("Chase")
            self.techfield.addItem("Braden")
            wofieldlayout.addWidget(self.techfield)

            #woentrylayout.addLayout(techlayout)

            woformlayout.addLayout(wopromptlayout)
            woformlayout.addLayout(wofieldlayout)

            woentrylayout.addLayout(woformlayout)

            self.runindbutton = QPushButton("Create Workorder")
            self.runindbutton.setMinimumWidth(200)
            self.runindbutton.setMaximumWidth(300)
            self.runindbutton.clicked.connect(self.RunIndividualTests)

            wobuttonlayout.addWidget(self.runindbutton)

            self.back = QPushButton("Back")
            self.back.setMinimumWidth(200)
            self.back.setMaximumWidth(300)
            self.back.clicked.connect(self.ReturnToMain)
            wobuttonlayout.addWidget(self.back)

            woentrylayout.addLayout(wobuttonlayout)


            layout.addLayout(woentrylayout)

            self.workorderentry.setLayout(layout)
        except Exception as e:
            print(f"Error as {e}")



    def OpenExistingWorkorder(self):
        try:
            self.openExistingWorkorder = True
            self.setMinimumSize(300, 200)

            self.openWorkorder = QWidget()
            self.setCentralWidget(self.openWorkorder)

            layout = QVBoxLayout()
            layout.setSpacing(5)



            openlayout = QVBoxLayout()
            openlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.wobuttonlayout = QHBoxLayout()
            self.wobuttonlayout.setSpacing(5)
            self.wobuttonlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            #self.wobuttonlayout.setContentsMargins(20, 0, 20, 0)

            self.workordernumberfield = QLineEdit()
            self.workordernumberfield.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.workordernumberfield.setContentsMargins(0,0,0,20)
            self.workordernumberfield.setMaximumWidth(400)
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
            self.workorderOpen.setMinimumWidth(200)
            self.workorderOpen.setMaximumWidth(300)
            self.workorderOpen.setProperty("class", "small")
            try:
                self.workorderOpen.clicked.connect(self.RunIndividualTests)
            except Exception as e:
                print(f"Error while opening workorder: {e}")
            self.wobuttonlayout.addWidget(self.workorderOpen)

            self.woopenback = QPushButton("Back")
            self.woopenback.setMinimumWidth(200)
            self.woopenback.setMaximumWidth(300)
            self.woopenback.setProperty("class", "small")
            self.woopenback.clicked.connect(self.ReturnToMain)
            self.wobuttonlayout.addWidget(self.woopenback)

            openlayout.addLayout(self.wobuttonlayout)
            layout.addLayout(openlayout)

            self.openWorkorder.setLayout(layout)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

    def Settings(self):
        self.setWindowTitle("Application Settings")
        self.settings = QWidget()
        self.setCentralWidget(self.settings)


        self.settingsLayout = QVBoxLayout()
        self.settings.setLayout(self.settingsLayout)

        self.optionsLayout = QHBoxLayout()

        self.descriptionLayout = QVBoxLayout()
        self.selectionLayout = QVBoxLayout()


        self.themeLabel = QLabel("Select Theme:")
        self.themeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.descriptionLayout.addWidget(self.themeLabel)

        self.themeSelection = QComboBox()
        self.themeSelection.currentTextChanged.connect(self.updateTheme)
        #self.themeSelection.addItem("Default")
        self.themeSelection.addItem("Bauhaus Pop")
        self.themeSelection.addItem("Brutalist Terminal")
        self.themeSelection.addItem("Retro Terminal")
        self.themeSelection.addItem("Concrete Pulse")
        self.themeSelection.addItem("Cream and Copper")
        self.themeSelection.addItem("Diamonds")
        self.themeSelection.addItem("Ever Reputation")
        self.themeSelection.addItem("Fenty")
        self.themeSelection.addItem("Glacier Glass")
        self.themeSelection.addItem("Glitchwave")
        self.themeSelection.addItem("Graphite and Mint")
        self.themeSelection.addItem("Midnight Neon")
        self.themeSelection.addItem("Minimal Blue")
        self.themeSelection.addItem("Move")
        self.themeSelection.addItem("Pastel Sketchbook")
        self.themeSelection.addItem("Verdant Grove")


        self. selectionLayout.addWidget(self.themeSelection)

        self.optionsLayout.addLayout(self.descriptionLayout)
        self.optionsLayout.addLayout(self.selectionLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.backButton = QPushButton("Back")
        self.backButton.setMinimumWidth(200)
        self.backButton.setMaximumWidth(300)
        self.backButton.setProperty("class", "small")
        self.backButton.clicked.connect(self.ReturnToMain)
        self.buttonLayout.addWidget(self.backButton)

        self.settingsLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settingsLayout.addLayout(self.optionsLayout)
        self.settingsLayout.addLayout(self.buttonLayout)

    def CloseWindow(self):
        print(my_instrument.write('OUTP 0'))
        print(my_instrument.write('VOLT 0'))



    def ReturnToMain(self):
        try:
            self.setWindowTitle("COMATS")
            # self.setFixedSize(800, 600)
            # self.theme = "Themes/MinimalBlue.qss"

            self.welcome = QWidget()
            self.setCentralWidget(self.welcome)
            # self.showFullScreen()

            self.welcomeLayout = QVBoxLayout()

            logoimage = "InAir"

            self.Logo = QPixmap(f"Images/{logoimage}.png")
            self.logoLabel = QLabel()
            self.logoLabel.setStyleSheet("""
                                padding-top: 0px;
                                padding-bottom: 20px;
                                padding-left: 100px;
                                padding-right: 100px;
                                    """)
            # self.logoLabel.setScaledContents(True)
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

            self.footerLayout = QHBoxLayout()

            self.settings = QPushButton("Settings")
            self.settings.setProperty("class", "small")
            self.settings.setFixedWidth(10)
            self.settings.setFixedHeight(30)
            self.settings.clicked.connect(self.Settings)
            self.footerLayout.addWidget(self.settings, alignment=Qt.AlignmentFlag.AlignLeft)

            self.version = QLabel("V. 2.0.1")
            self.version.setStyleSheet("""
                                        font-size:12px;
                                        """)
            self.version.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.footerLayout.addWidget(self.version)

            self.welcomeLayout.addLayout(self.footerLayout)



        except Exception as e:
            print(f"Error while returning to main: {e}")


    def RunIndividualTests(self):
        if self.createNewWorkorder:
            modelNumber = self.workordermodelfield.currentText()
        elif self.openExistingWorkorder:
            modelNumber = self.GetUnitModel(workorder_filename=f"{self.workordernumberfield.text()}.txt")
            print(modelNumber)

        if modelNumber == "11225-1":
            try:
                self.runIndividualTests11225 = True
                self.setMinimumSize(1150, 700)

                self.visualinspection_test = VisualInspectionTest(self.inst_worker)
                self.lowwater_test = LowWaterTest(self.inst_worker)
                self.waterleaks_test = WaterLeaksTest(self.inst_worker)
                self.heatercurrent_test = HeaterCurrentTest(self.inst_worker)
                self.hotwaterlight_test = HotWaterLightTest(self.inst_worker)
                self.brewbe_test = BrewBETest(self.inst_worker)
                self.watertemp_test = WaterTempTest(self.inst_worker)
                self.temperature_test = TemperatureTest(self.inst_worker)
                self.ambienttemp_test = AmbientTemperatureTest(self.inst_worker)
                self.heatedwater_test = HeatedWaterTest(self.inst_worker)
                self.unheatedwater_test = UnheatedWaterTest(self.inst_worker)
                self.lamp_test = LampTest(self.inst_worker)
                self.hotplate_test = HotPlateTest(self.inst_worker)
                self.powerinterrupt_test = PowerInterruptTest(self.inst_worker)
                self.brewinterrupt_test = BrewInterruptTest(self.inst_worker)
                self.iredmonitor_test = IREDMonitorTest(self.inst_worker)
                self.pressurereliefvalve_test = PressureReliefValveTest(self.inst_worker)

            except Exception as e:
                print(f"Error while creating V.Inspect: {e}")

        elif modelNumber == "4810-28UG-00":
            self.runIndividualTests4810 = True
            self.setMinimumSize(1150, 700)

            self.dielectric_test = DielectricTest(self.inst_worker)
            self.resistance_test = ResistanceTest(self.inst_worker)
            self.watertemp_test = WaterTempTest(self.inst_worker)
            self.ambienttemp_test = AmbientTemperatureTest(self.inst_worker)
            self.tankpressure_test = TankPressureTest(self.inst_worker)
            self.powerandlowlight_test = PowerAndLowLightTest(self.inst_worker)
            self.rtdcircuit_test = RTDCircuitTest(self.inst_worker)
            self.heaterandpreheater_test = HeaterAndPreheaterTest(self.inst_worker)
            self.brew_test = BrewTest(self.inst_worker)
            self.serverretainer_test = ServerRetainerTest(self.inst_worker)
            self.tea_test = TeaTest(self.inst_worker)


        try:
            workorder_file = f"{self.workordernumberfield.text()}.txt"
            test_path = os.path.join("Tests/", workorder_file)
            print(test_path)
        except Exception as e:
            print(f"Error while opening workorder file: {e}")
        if modelNumber == "11225-1":
            try:
                self.visualinspection_test.VisualInspectionTestPath(test_path)
                self.lowwater_test.LowWaterTestPath(test_path)
                self.waterleaks_test.WaterLeaksTestPath(test_path)
                self.heatercurrent_test.HeaterCurrentTestPath(test_path)
                self.brewbe_test.BrewBETestPath(test_path)
                self.temperature_test.TemperatureTestPath(test_path)
                self.heatedwater_test.HeatedWaterTestPath(test_path)
                self.unheatedwater_test.UnheatedWaterTestPath(test_path)
                self.lamp_test.LampTestPath(test_path)
                self.hotplate_test.HotPlateTestPath(test_path)
                self.powerinterrupt_test.PowerInterruptTestPath(test_path)
                self.brewinterrupt_test.BrewInterruptTestPath(test_path)
                self.iredmonitor_test.IREDMonitorTestPath(test_path)

            except Exception as e:
                print(f"Error while setting test path: {e}")
        elif modelNumber == "4810-28UG-00":
            try:
                self.resistance_test.ResistanceTestPath(test_path)
                self.dielectric_test.DielectricTestPath(test_path)
                self.watertemp_test.WaterTempTestPath(test_path)
                self.ambienttemp_test.AmbientTempTestPath(test_path)
                self.tankpressure_test.TankPressureTestPath(test_path)
                self.powerandlowlight_test.PowerAndLowLightTestPath(test_path)
                self.rtdcircuit_test.RTDCircuitTestPath(test_path)
                self.heaterandpreheater_test.HeaterAndPreheaterTestPath(test_path)
                self.brew_test.BrewTestPath(test_path)
                self.serverretainer_test.ServerRetainerTestPath(test_path)
                self.tea_test.TeaTestPath(test_path)
            except Exception as E:
                print(f"Error while opening workorder file 1: {E}")
        try:
            if not os.path.exists(test_path):
                with open(f"{test_path}", "w") as file:
                    file.write(f"Workorder Number: {self.workordernumberfield.text()}\n"
                                f"Unit Number: {self.workordermodelfield.currentText()}\n"
                                f"Unit Serial Number: {self.serialnumberfield.text()}\n"
                                f"Unit Part Number: {self.unitpartnumberfield.text()}\n"
                                f"Technician Name: {self.techfield.currentText()}\n\n\n")

                    if modelNumber == "11225-1":
                        try:
                            file.write("Creating a 11225-1 Test File"
                                   "\n\n"
                                   "_Functional Tests_"
                                   "\n\n"
                                   ">>Visual Inspection Test<<"
                                   "\n"
                                   f"{self.visualinspection_test.GetVisualInspectionResults()}"
                                   "\n\n"
                                   ">>Low Water Test<<"
                                   "\n"
                                   f"{self.lowwater_test.GetLowWaterResults()}"
                                   "\n\n"
                                   ">>Water Leaks Inspection Test<<"
                                   "\n"
                                   f"{self.waterleaks_test.GetWaterLeaksResults()}"
                                   "\n\n"
                                   ">>Heater Current Test<<"
                                   "\n"
                                   f"{self.heatercurrent_test.GetHeaterCurrentResults()}"
                                   "\n\n"
                                   ">>Hot Water Light Test<<"
                                   "\n"
                                   f"{self.hotwaterlight_test.GetHotWaterLightPressureResults()}"
                                   "\n\n"
                                   ">>Brew Test<<"
                                   "\n"
                                   f"{self.brewbe_test.GetBrewBEResults()}"
                                   "\n>>Temperature Test<<"
                                   "\n"
                                   f"{self.temperature_test.GetTemperatureTestResults()}"
                                   "\n\n"
                                   ">>Heated Water Test<<"
                                   "\n"
                                   f"{self.heatedwater_test.GetHeatedWaterResults()}"
                                   "\n\n"
                                   ">>Unheated Water Test<<"
                                   "\n"
                                   f"{self.unheatedwater_test.GetUnheatedWaterResults()}"
                                   "\n\n"
                                   ">>Lamp Test<<"
                                   "\n"
                                   f"{self.lamp_test.GetLampResults()}"
                                   "\n\n"
                                   ">>Hot Plate Test<<"
                                   "\n"
                                   f"{self.hotplate_test.GetHotPlateResults()}"
                                    "\n\n"
                                    ">>Power Interrupt Test<<"
                                    "\n"
                                    f"{self.powerinterrupt_test.GetPowerInterruptResults()}"
                                    "\n\n"
                                    ">>Brew Interrupt Test<<"
                                    "\n"
                                    f"{self.brewinterrupt_test.GetBrewInterruptResults()}"
                                    "\n\n"
                                    ">>IRED Monitor Test<<"
                                    "\n"
                                    f"{self.iredmonitor_test.GetIREDMonitorResults()}"
                                    "\n\n"
                                    ">>Pressure Relief Valve Test<<"
                                    "\n"
                                    f"{self.pressurereliefvalve_test.GetPressureReliefValveResults()}"
                                   )
                        except Exception as e:
                            print(f"Error while writing V.Inspect File: ")
                    elif modelNumber == "4810-28UG-00":
                        file.write("Creating a 4810-UG-00 Test File"
                                   "\n\n"
                                   "_Functional Tests_"
                                   "\n\n"
                                   ">>Dielectric Test<<"
                                   "\n"
                                   f"{self.dielectric_test.GetDielectricResults()}"
                                   "\n\n"
                                   ">>Resistance Test<<"
                                   "\n"
                                   f"{self.resistance_test.GetResistanceResults()}"
                                   "\n\n"
                                   ">>Water Supply Temperature Test<<"
                                   "\n"
                                   f"{self.watertemp_test.GetWaterTempResults()}"
                                   "\n\n"
                                   ">>Ambient Temperature Test<<"
                                   "\n"
                                   f"{self.ambienttemp_test.GetAmbientTempResults()}"
                                   "\n\n"
                                   ">>Tank Pressure Test<<"
                                   "\n"
                                   f"{self.tankpressure_test.GetTankPressureResults()}"
                                   "\n\n"
                                   ">>Power and Low Indicator Light Test<<"
                                   "\n"
                                   f"{self.powerandlowlight_test.GetPowerAndLowLightResults()}"
                                   "\n\n"
                                   ">>RTD Test<<"
                                   "\n"
                                   f"{self.rtdcircuit_test.GetRTDCircuitTestResults()}"
                                   "\n\n"
                                   ">>Tank Heater and Preheater Test<<"
                                   "\n"
                                   f"{self.heaterandpreheater_test.GetHeaterAndPreheaterResults()}"
                                   "\n\n"
                                   ">>Brew Test<<"
                                   "\n"
                                   f"{self.brew_test.GetBrewResults()}"
                                   "\n\n"
                                   ">>Server Retainer Test<<"
                                   "\n"
                                   f"{self.serverretainer_test.GetServerRetainerResults()}"
                                   "\n\n"
                                   ">>Tea Test<<"
                                   "\n"
                                   f"{self.tea_test.GetTeaResults()}"
                                   )
            """else:
                try:
                    with open(f"{test_path}", "r") as file:
                        lines = file.readlines()
                        print(len(lines))
                    with open(f"{test_path}", "a+") as file:
                        if len(lines) <= 6:
                            if modelNumber == "11225-1":
                                file.write("Creating a 11225-1 Test File"
                                        "\n\n"
                                    "_Functional Tests_"
                                    "\n\n"
                                    ">>Dielectric Test<<"
                                    "\n"
                                    f"{self.dielectric_test.GetDielectricResults()}"
                                    "\n\n"
                                    ">>Resistance Test<<"
                                    "\n"
                                    f"{self.resistance_test.GetResistanceResults()}"
                                    "\n\n"
                                    ">>Water Supply Temperature Test<<"
                                    "\n"
                                    f"{self.watertemp_test.GetWaterTempResults()}"
                                    "\n\n"
                                    ">>Ambient Temperature Test<<"
                                    "\n"
                                    f"{self.ambienttemp_test.GetAmbientTempResults()}"
                                    "\n\n"
                                    ">>Tank Pressure Test<<"
                                    "\n"
                                    f"{self.tankpressure_test.GetTankPressureResults()}"
                                    "\n\n"
                                    ">>Power and Low Indicator Light Test<<"
                                    "\n"
                                    f"{self.powerandlowlight_test.GetPowerAndLowLightResults()}"
                                    "\n\n"
                                    ">>RTD Test<<"
                                    "\n"
                                    f"{self.rtdcircuit_test.GetRTDCircuitTestResults()}"
                                    "\n\n"
                                    ">>Tank Heater and Preheater Test<<"
                                    "\n"
                                    f"{self.heaterandpreheater_test.GetHeaterAndPreheaterResults()}"
                                    "\n\n"
                                    ">>Brew Test<<"
                                    "\n"
                                    f"{self.brew_test.GetBrewResults()}"
                                    "\n\n"
                                    ">>Server Retainer Test<<"
                                    "\n"
                                    f"{self.serverretainer_test.GetServerRetainerResults()}"
                                   "\n\n"
                                   ">>Tea Test<<"
                                   "\n"
                                   f"{self.tea_test.GetTeaResults()}"
                                   )
                            elif modelNumber == "4810-28UG-00":
                                file.write("Creating a 4810-UG-00 Test File"
                                            "\n\n"
                                           "_Functional Tests_"
                                           "\n\n"
                                           ">>Dielectric Test<<"
                                           "\n"
                                           f"{self.dielectric_test.GetDielectricResults()}"
                                           "\n\n"
                                           ">>Resistance Test<<"
                                           "\n"
                                           f"{self.resistance_test.GetResistanceResults()}"
                                           "\n\n"
                                           ">>Water Supply Temperature Test<<"
                                           "\n"
                                           f"{self.watertemp_test.GetWaterTempResults()}"
                                           "\n\n"
                                           ">>Ambient Temperature Test<<"
                                           "\n"
                                           f"{self.ambienttemp_test.GetAmbientTempResults()}"
                                           "\n\n"
                                           ">>Tank Pressure Test<<"
                                           "\n"
                                           f"{self.tankpressure_test.GetTankPressureResults()}"
                                           "\n\n"
                                           ">>Power and Low Indicator Light Test<<"
                                           "\n"
                                           f"{self.powerandlowlight_test.GetPowerAndLowLightResults()}"
                                           "\n\n"
                                           ">>RTD Test<<"
                                           "\n"
                                           f"{self.rtdcircuit_test.GetRTDCircuitTestResults()}"
                                           "\n\n"
                                           ">>Tank Heater and Preheater Test<<"
                                           "\n"
                                           f"{self.heaterandpreheater_test.GetHeaterAndPreheaterResults()}"
                                           "\n\n"
                                           ">>Brew Test<<"
                                           "\n"
                                           f"{self.brew_test.GetBrewResults()}"
                                           "\n\n"
                                           ">>Server Retainer Test<<"
                                           "\n"
                                           f"{self.serverretainer_test.GetServerRetainerResults()}"
                                           "\n\n"
                                           ">>Tea Test<<"
                                           "\n"
                                           f"{self.tea_test.GetTeaResults()}"
                                           )



                except Exception as e:
                    print(f"error opening wo: {e}")"""

        except Exception as e:
            print(f"error opening wo: {e}")


        # Create QTabWidget
        try:
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)
        except Exception as e:
            print(f"error opening wo: {e}")


        # Create 10 tabs
        if modelNumber == "11225-1":
            try:
            #self.tabs.addTab(self, "11225")
                self.tabs.addTab(self.visualinspection_test, "Visual Inspection")
                self.tabs.addTab(self.lowwater_test, "Low Water")
                self.tabs.addTab(self.waterleaks_test, "Water Leaks")
                self.tabs.addTab(self.heatercurrent_test, "Heater Current")
                self.tabs.addTab(self.hotwaterlight_test, "Hot Water Light")
                self.tabs.addTab(self.brewbe_test, "Brew")
                self.tabs.addTab(self.temperature_test, "Temperature Test")
                self.tabs.addTab(self.heatedwater_test, "Heated Water")
                self.tabs.addTab(self.unheatedwater_test, "Unheated Water")
                self.tabs.addTab(self.lamp_test, "Lamp")
                self.tabs.addTab(self.hotplate_test, "Hot Plate")
                self.tabs.addTab(self.powerinterrupt_test, "Power Interrupt")
                self.tabs.addTab(self.brewinterrupt_test, "Brew Interrupt")
                self.tabs.addTab(self.iredmonitor_test, "IRED Monitor")
                self.tabs.addTab(self.pressurereliefvalve_test, "Pressure Relief Valve")

                #self.tabs.addTab(self.dielectric_test, f"Dielectric 11225")
                #self.tabs.addTab(self.resistance_test, f"Resistance")
                #self.tabs.addTab(self.watertemp_test, f"Water Supply Temperature")
                #self.tabs.addTab(self.ambienttemp_test, f"Ambient Temperature")
                #self.tabs.addTab(self.tankpressure_test, f"Tank Pressure")
                #self.tabs.addTab(self.powerandlowlight_test, f"Power and Low Light Indicator")
                #self.tabs.addTab(self.rtdcircuit_test, f"RTD Circuit")
                #self.tabs.addTab(self.heaterandpreheater_test, f"Tank Heater and Preheater")
                #self.tabs.addTab(self.brew_test, f"Brew")
                #self.tabs.addTab(self.serverretainer_test, f"Server Retainer")
                #self.tabs.addTab(self.tea_test, f"Tea")
            except Exception as e:
                print(f"Error while adding tab: {e}")
        if modelNumber == "4810-28UG-00":
            try:
            #self.tabs.addTab(self, "11225")
                self.tabs.addTab(self.dielectric_test, f"Dielectric 4810-UG-00")
                self.tabs.addTab(self.resistance_test, f"Resistance")
                self.tabs.addTab(self.watertemp_test, f"Water Supply Temperature")
                self.tabs.addTab(self.ambienttemp_test, f"Ambient Temperature")
                self.tabs.addTab(self.tankpressure_test, f"Tank Pressure")
                self.tabs.addTab(self.powerandlowlight_test, f"Power and Low Light Indicator")
                self.tabs.addTab(self.rtdcircuit_test, f"RTD Circuit")
                self.tabs.addTab(self.heaterandpreheater_test, f"Tank Heater and Preheater")
                self.tabs.addTab(self.brew_test, f"Brew")
                self.tabs.addTab(self.serverretainer_test, f"Server Retainer")
                self.tabs.addTab(self.tea_test, f"Tea")
            except Exception as e:
                print(f"Error while adding tab: {e}")

    def GetUnitModel(self, workorder_filename):
        try:
            with open(f"Tests/{workorder_filename}", "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("Unit Number:"):
                        # Strip and split to get the value after the colon
                        return line.split(":", 1)[1].strip()
        except FileNotFoundError:
            print(f"File Tests/{workorder_filename} not found.")
        return None

    def updateTheme(self, theme_name):
        self.theme = theme_name
        self.theme = self.theme.replace(" ", "")
        print(self.theme)
        print("Index changed")
        try:
            with open(f"Themes/{self.theme}.qss", "r", encoding="utf-8") as f:
                qss = f.read()
                app.setStyleSheet(qss)  # use stored reference
                print(f"Theme updated to: {self.theme}")
        except FileNotFoundError:
            print(f"Theme file Themes/{self.theme}.qss not found.")


# === Application entry point ===
if __name__ == "__main__":
    app = QApplication(sys.argv)

    theme = ""
    try:
        with open(f"Themes/{theme}.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Failed to load default theme: {e}")

    window = MainWindow()
    window.app = app  # pass app reference to the window
    window.theme = theme
    window.show()

    sys.exit(app.exec())


