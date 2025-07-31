import sys
import os

from PyQt6.QtGui import QPixmap, QFontDatabase, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLineEdit
)

from PyQt6.QtWidgets import QTabBar
from PyQt6.QtCore import QSize


from PyQt6.QtCore import Qt, pyqtSignal, QObject
#from PyQt6.QtWidgets.QWidget import setWindowFlag

from Dielectric import DielectricTest
from Resistance import ResistanceTest
from AmbientTemp import AmbientTemperatureTest
from WaterSupplyTemperature import WaterTempTest
from TankPressure import TankPressureTest
from ServerRetainer import ServerRetainerTest
from Brew import BrewTest
from HeaterAndPreheater import HeaterAndPreheaterTest
from RTDCircuit import RTDCircuitTest
from PowerAndLowLight import PowerAndLowLightTest


#import pyvisa


#--------------------------------------- Test Instances



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
        #self.theme = "Themes/MinimalBlue.qss"

        self.welcome = QWidget()
        self.setCentralWidget(self.welcome)
        #self.showFullScreen()

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
        #self.logoLabel.setScaledContents(True)
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
            self.setMinimumSize(400, 200)

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
            self.setMinimumSize(300, 200)

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
            self.workorderOpen.setProperty("class", "small")
            self.workorderOpen.clicked.connect(self.RunIndividualTests)
            self.wobuttonlayout.addWidget(self.workorderOpen)

            self.woopenback = QPushButton("Back")
            self.woopenback.setProperty("class", "small")
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
        self.setMinimumSize(1150, 600)

        self.dielectric_test = DielectricTest()
        self.resistance_test = ResistanceTest()
        self.watertemp_test = WaterTempTest()
        self.ambienttemp_test = AmbientTemperatureTest()
        self.tankpressure_test = TankPressureTest()
        self.powerandlowlight_test = PowerAndLowLightTest()
        self.rtdcircuit_test = RTDCircuitTest()
        self.heaterandpreheater_test = HeaterAndPreheaterTest()
        self.brew_test = BrewTest()
        self.serverretainer_test = ServerRetainerTest()


        workorder_file = f"{self.workordernumberfield.text()}.txt"
        test_path = os.path.join("Tests/", workorder_file)
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
        except Exception as e:
            print(f"Error while setting test_path: {e}")
        if not os.path.exists(test_path):
            with open(f"{test_path}", "w") as file:
                file.write(f"Workorder Number: {self.workordernumberfield.text()}\n"
                            f"Unit Serial Number: {self.serialnumberfield.text()}\n"
                            f"Part Number: {self.unitpartnumberfield.text()}\n"
                            f"Technician Name: {self.techfield.text()}\n\n\n")
        else:
            try:
                with open(f"{test_path}", "r") as file:
                    lines = file.readlines()
                    print(len(lines))
                with open(f"{test_path}", "a+") as file:
                    if len(lines) <= 6:
                        file.write("\n\n"
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
                                   )



            except Exception as e:
                print(f"error opening wo: {e}")


        # Create QTabWidget
        if (self.runIndividualTests == True):
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)




        # Create 10 tabs
        try:

            self.tabs.addTab(self.dielectric_test, f"Dielectric")
            self.tabs.addTab(self.resistance_test, f"Resistance")
            self.tabs.addTab(self.watertemp_test, f"Water Supply Temperature")
            self.tabs.addTab(self.ambienttemp_test, f"Ambient Temperature")
            self.tabs.addTab(self.tankpressure_test, f"Tank Pressure")
            self.tabs.addTab(self.powerandlowlight_test, f"Power and Low Light Indicator")
            self.tabs.addTab(self.rtdcircuit_test, f"RTD Circuit")
            self.tabs.addTab(self.heaterandpreheater_test, f"Tank Heater and Preheater")
            self.tabs.addTab(self.brew_test, f"Brew")
            self.tabs.addTab(self.serverretainer_test, f"Server Retainer")
        except Exception as e:
            print(f"Error while adding tab: {e}")



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




# === Application entry point ===
if __name__ == "__main__":
    app = QApplication(sys.argv)

    theme = "RetroTerminal"
    with open(f"Themes/{theme}.qss", "r") as f:
        app.setStyleSheet(f.read())

    # Load the font so Qt can recognize the name in QSS
    font_id = QFontDatabase.addApplicationFont("fonts/Staatliches-Regular.ttf.ttf")
    if font_id != -1:
        loaded_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        print(f"Loaded font: {loaded_font_family}")
    else:
        print("Failed to load custom font.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

