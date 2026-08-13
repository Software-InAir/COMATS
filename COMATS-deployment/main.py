import sys
import os
import subprocess
import platform
import requests
import traceback

from pathlib import Path

from PyQt6 import *

from PyQt6.QtGui import QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLineEdit, QComboBox)
from PyQt6.QtCore import QThread, Qt, QUrl

import pyvisa

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
from Lamp import LampTest
from HotPlate import HotPlateTest
from BrewInterrupt import BrewInterruptTest
from IREDMonitor import IREDMonitorTest
from PressureReliefValve import PressureReliefValveTest

from Python.Automation.BDaq.InstantDoCtrl import InstantDoCtrl

def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path.joinpath(*parts)

#do = InstantDoCtrl("PCIE-1761H,BID#0")

#Pump on relay command
#ret = do.writeAny(0, 1, [0x01])

USE_INSTRUMENT = False

if USE_INSTRUMENT:
    rm = pyvisa.ResourceManager()

    my_instrument = rm.open_resource('GPIB0::3::INSTR')
    my_instrument.write('COUP DIRECT')
    my_instrument.write('CURR:LIM 9.0')
    my_instrument.write('PROT:STAT 1')
    my_instrument.write('CURR:PROT:LEV 9.1')



    my_instrument.write('OUTP 1')
    my_instrument.write('VOLT 115')
    my_instrument.write('FREQ 400')
    my_instrument.query('OUTP?')



# === Main application window ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme = "Default"
        self.setWindowTitle("COMATS")
        self.setFixedSize(1280, 635)


        self.api_base_url = "http://100.125.162.6:8000"
        self.current_test_id = None


        self.welcome = QWidget()
        self.setCentralWidget(self.welcome)
        #self.showFullScreen()

        self.welcomeLayout = QVBoxLayout()

        logoimage = "InAir"

        self.Logo = QPixmap(str(resource_path("Images", "InAir.png")))
        self.logoLabel = QLabel()
        self.logoLabel.setPixmap(self.Logo)
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logoLabel.setContentsMargins(100, 0, 100, 40)
        self.welcomeLayout.addWidget(self.logoLabel)


        self.welcomeLabel = QLabel("Welcome to COMATS")
        self.welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcomeLabel.setContentsMargins(100, 0, 100, 40)
        self.welcomeLayout.addWidget(self.welcomeLabel)
        self.welcomeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.welcome.setLayout(self.welcomeLayout)


        if USE_INSTRUMENT:
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

        else:
            self.inst_thread = None
            self.inst_worker = None

        # --- Build tabs, pass the worker reference ---

        self.createNewWorkorder = False
        self.openExistingWorkorder = False

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

        self.settings.setFixedHeight(30)
        self.settings.clicked.connect(self.Settings)
        self.footerLayout.addWidget(self.settings, alignment=Qt.AlignmentFlag.AlignLeft)

        self.version = QLabel("V. 2.0.1")
        self.version.setStyleSheet("""
                            font-size:12px;
                            """)
        self.version.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.footerLayout.addWidget(self.version)


        self.welcomeLayout.addLayout(self.buttonLayout)

        self.welcomeLayout.addSpacing(100)

        self.welcomeLayout.addLayout(self.footerLayout)


    def closeEvent(self, event):
        if USE_INSTRUMENT:
            my_instrument.write('VOLT 0')
            my_instrument.query('OUTP 0')
        do = InstantDoCtrl("PCIE-1761H,BID#0")

        # Pump on relay command
        ret = do.writeAny(0, 1, [0x00])
        print(ret)


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
            self.workordermodelfield.addItem("4510-28UG-00")
            self.workordermodelfield.addItem("4510-44UG-00")
            wofieldlayout.addWidget(self.workordermodelfield)

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
            self.techfield.addItem("Zack")
            self.techfield.addItem("Temporary Technician")
            self.techfield.addItem("Engineering")
            wofieldlayout.addWidget(self.techfield)

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
            self.workorderOpen.clicked.connect(self.RunIndividualTests)
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

        self.selectionLayout.addWidget(self.themeSelection)

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


    def ReturnToMain(self):
        try:
            self.setWindowTitle("COMATS")

            self.welcome = QWidget()
            self.setCentralWidget(self.welcome)
            # self.showFullScreen()

            self.welcomeLayout = QVBoxLayout()

            logoimage = "InAir"

            self.Logo = QPixmap(str(resource_path("Images", "InAir.png")))
            self.logoLabel = QLabel()
            self.logoLabel.setStyleSheet("""
                                padding-top: 0px;
                                padding-bottom: 20px;
                                padding-left: 100px;
                                padding-right: 100px;
                                    """)

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

            self.createNewWorkorder = False
            self.openExistingWorkorder = False

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

        try:
            wo_number = self.workordernumberfield.text().strip()
            serial_number = (self.serialnumberfield.text().strip()
                             if self.createNewWorkorder
                             else ""
                             )
            technician = (self.techfield.currentText().strip()
                          if self.createNewWorkorder
                          else ""
                          )
            if modelNumber == "11225-1":
                model_code = "MODEL_A"
            elif modelNumber == "4510-28UG-00" or modelNumber == "4510-44UG-00":
                model_code = "MODEL_B"

            payload = {
                "wo_number": wo_number,
                "model_code": model_code,
                "serial_number": serial_number,
                "technician": technician,
            }

            url = f"{self.api_base_url}/tests"
            r = requests.post(url, json=payload, timeout=5)
            print("Create test status:", r.status_code)
            print("Create test response:", r.text)
            r.raise_for_status()
            data = r.json()
            self.current_test_id = data.get("id")

        except Exception as e:
            print(f"Error creating test with API: {e}")
            self.current_test_id = None

            # Create QTabWidget

        try:
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)
        except Exception as e:
            print(f"error opening wo: {e}")

        if modelNumber == "11225-1":
            try:
                self.setMinimumSize(1150, 700)

                self.visualinspection_test = VisualInspectionTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.visualinspection_test, "set_test_context"
                ):
                    self.visualinspection_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.lowwater_test = LowWaterTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.lowwater_test, "set_test_context"
                ):
                    self.lowwater_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.waterleaks_test = WaterLeaksTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.waterleaks_test, "set_test_context"
                ):
                    self.waterleaks_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.heatercurrent_test = HeaterCurrentTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.heatercurrent_test, "set_test_context"
                ):
                    self.heatercurrent_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.hotwaterlight_test = HotWaterLightTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.hotwaterlight_test, "set_test_context"
                ):
                    self.hotwaterlight_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.brewbe_test = BrewBETest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.brewbe_test, "set_test_context"
                ):
                    self.brewbe_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.watertemp_test = WaterTempTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.watertemp_test, "set_test_context"
                ):
                    self.watertemp_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.temperature_test = TemperatureTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.temperature_test, "set_test_context"
                ):
                    self.temperature_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.ambienttemp_test = AmbientTemperatureTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.ambienttemp_test, "set_test_context"
                ):
                    self.ambienttemp_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.heatedwater_test = HeatedWaterTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.heatedwater_test, "set_test_context"
                ):
                    self.heatedwater_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )

                self.lamp_test = LampTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.lamp_test, "set_test_context"
                ):
                    self.lamp_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.hotplate_test = HotPlateTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.hotplate_test, "set_test_context"
                ):
                    self.hotplate_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.powerinterrupt_test = PowerInterruptTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.powerinterrupt_test, "set_test_context"
                ):
                    self.powerinterrupt_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.brewinterrupt_test = BrewInterruptTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                    self.brewinterrupt_test, "set_test_context"
                ):
                    self.brewinterrupt_test.set_test_context(
                        self.current_test_id, self.api_base_url
                )
                self.iredmonitor_test = IREDMonitorTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.iredmonitor_test, "set_test_context"
                ):
                    self.iredmonitor_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                self.pressurereliefvalve_test = PressureReliefValveTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.pressurereliefvalve_test, "set_test_context"
                ):
                    self.pressurereliefvalve_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
            except Exception as e:
                print(f"Error while creating V.Inspect: {e}")
                traceback.print_exc()

        elif modelNumber == "4510-28UG-00" or modelNumber == "4510-44UG-00":
            try:
                self.setMinimumSize(1150, 700)

                self.dielectric_test = DielectricTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.dielectric_test, "set_test_context"
                ):
                    self.dielectric_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Dielectric")

                self.resistance_test = ResistanceTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.resistance_test, "set_test_context"
                ):
                    self.resistance_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Resistance")

                self.watertemp_test = WaterTempTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.watertemp_test, "set_test_context"
                ):
                    self.watertemp_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Water Temp")

                self.ambienttemp_test = AmbientTemperatureTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.ambienttemp_test, "set_test_context"
                ):
                    self.ambienttemp_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Resistance")

                self.tankpressure_test = TankPressureTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.tankpressure_test, "set_test_context"
                ):
                    self.tankpressure_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Tank Pressure")

                self.powerandlowlight_test = PowerAndLowLightTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.powerandlowlight_test, "set_test_context"
                ):
                    self.powerandlowlight_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Power and Low Light")

                self.rtdcircuit_test = RTDCircuitTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.rtdcircuit_test, "set_test_context"
                ):
                    self.rtdcircuit_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to RTD Circuit")

                self.heatedwater_test = HeatedWaterTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.heatedwater_test, "set_test_context"
                ):
                    self.heatedwater_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )

                self.hotplate_test = HotPlateTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.hotplate_test, "set_test_context"
                ):
                    self.hotplate_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )

                self.heaterandpreheater_test = HeaterAndPreheaterTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.heaterandpreheater_test, "set_test_context"
                ):
                    self.heaterandpreheater_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Heater and Preheater")

                self.brew_test = BrewTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.brew_test, "set_test_context"
                ):
                    self.brew_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Brew")

                self.serverretainer_test = ServerRetainerTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.serverretainer_test, "set_test_context"
                ):
                    self.serverretainer_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Server Retainer")

                self.tea_test = TeaTest(self.inst_worker, tabs=self.tabs)
                if self.current_test_id is not None and hasattr(
                        self.tea_test, "set_test_context"
                ):
                    self.tea_test.set_test_context(
                        self.current_test_id, self.api_base_url
                    )
                print("[MainWindow] Passed context to Tea")

            except Exception as e:
                print(f"Error while creating 4510: {e}")


        try:
            workorder_file = f"{self.workordernumberfield.text()}.txt"
            test_path = os.path.join("Tests\\", workorder_file)
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
                self.lamp_test.LampTestPath(test_path)
                self.hotplate_test.HotPlateTestPath(test_path)
                self.powerinterrupt_test.PowerInterruptTestPath(test_path)
                self.brewinterrupt_test.BrewInterruptTestPath(test_path)
                self.iredmonitor_test.IREDMonitorTestPath(test_path)
                self.hotwaterlight_test.HotWaterLightTestPath(test_path)
                self.pressurereliefvalve_test.PressureReliefValveTestPath(test_path)

            except Exception as e:
                print(f"Error while setting test path: {e}")
        elif modelNumber == "4510-28UG-00" or modelNumber == "4510-44UG-00":
            try:
                self.resistance_test.ResistanceTestPath(test_path)
                self.dielectric_test.DielectricTestPath(test_path)
                self.watertemp_test.WaterTempTestPath(test_path)
                self.ambienttemp_test.AmbientTempTestPath(test_path)
                self.tankpressure_test.TankPressureTestPath(test_path)
                self.powerandlowlight_test.PowerAndLowLightTestPath(test_path)
                self.rtdcircuit_test.RTDCircuitTestPath(test_path)
                self.heatedwater_test.HeatedWaterTestPath(test_path)
                self.hotplate_test.HotPlateTestPath(test_path)
                self.heaterandpreheater_test.HeaterAndPreheaterTestPath(test_path)
                self.brew_test.BrewTestPath(test_path)
                self.serverretainer_test.ServerRetainerTestPath(test_path)
                self.tea_test.TeaTestPath(test_path)
            except Exception as e:
                print(f"Error while opening workorder file 1: {e}")
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
                            file.write(
                                "Creating a 11225-1 Test File\n\n"
                                "_Functional Tests_\n\n"
                                ">>Visual Inspection Test<<\n\n"
                                ">>Low Water Test<<\n\n"
                                ">>Water Leaks Inspection Test<<\n\n"
                                ">>Heater Current Test<<\n\n"
                                ">>Hot Water Light Test<<\n\n"
                                ">>Brew Test<<\n\n"
                                ">>Temperature Test<<\n\n"
                                ">>Heated Water Test<<\n\n"
                                ">>Lamp Test<<\n\n"
                                ">>Hot Plate Test<<\n\n"
                                ">>Power Interrupt Test<<\n\n"
                                ">>Brew Interrupt Test<<\n\n"
                                ">>IRED Monitor Test<<\n\n"
                                ">>Pressure Relief Valve Test<<\n\n"
                            )
                        except Exception as e:
                            print(f"Error while writing V.Inspect File: ")
                    elif modelNumber == "4510-28UG-00" or modelNumber == "4510-44UG-00":
                        file.write(
                                   "\n\n"
                                   "_Functional Tests_"
                                   "\n\n"
                                   ">>Dielectric Test<<"
                                   "\n\n"
                                   ">>Resistance Test<<"
                                   "\n\n"
                                   ">>Water Supply Temperature Test<<"
                                   "\n\n"
                                   ">>Ambient Temperature Test<<"
                                   "\n\n"
                                   ">>Tank Pressure Test<<"
                                   "\n\n"
                                   ">>Power and Low Indicator Light Test<<"
                                   "\n\n"
                                   ">>RTD Test<<"
                                   "\n\n"
                                   ">>Heated Water Test<<"
                                   "\n\n"
                                   ">>Hot Plate Test<<"
                                   "\n\n"
                                   ">>Tank Heater and Preheater Test<<"
                                   "\n\n"
                                   ">>Brew Test<<"
                                   "\n\n"
                                   ">>Server Retainer Test<<"
                                   "\n\n"
                                   ">>Tea Test<<"
                                   )

        except Exception as e:
            print(f"error opening wo: {e}")





        # Create 10 tabs
        if modelNumber == "11225-1":
            try:
                self.tabs.addTab(self.visualinspection_test, "Visual Inspection")
                self.tabs.addTab(self.lowwater_test, "Low Water")
                self.tabs.addTab(self.waterleaks_test, "Water Leaks")
                self.tabs.addTab(self.heatercurrent_test, "Heater Current")
                self.tabs.addTab(self.hotwaterlight_test, "Hot Water Light")
                self.tabs.addTab(self.temperature_test, "Temperature Test")
                self.tabs.addTab(self.brewbe_test, "Brew")
                self.tabs.addTab(self.heatedwater_test, "Heated Water")
                self.tabs.addTab(self.lamp_test, "Lamp")
                self.tabs.addTab(self.hotplate_test, "Hot Plate")
                self.tabs.addTab(self.powerinterrupt_test, "Power Interrupt")
                self.tabs.addTab(self.brewinterrupt_test, "Brew Interrupt")
                self.tabs.addTab(self.iredmonitor_test, "IRED Monitor")
                self.tabs.addTab(self.pressurereliefvalve_test, "Pressure Relief Valve")

            except Exception as e:
                print(f"Error while adding tab: {e}")

        if modelNumber == "4510-28UG-00" or modelNumber == "4510-44UG-00":
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
                self.tabs.addTab(self.tea_test, f"Tea")
                self.tabs.addTab(self.heatedwater_test, "Heated Water")
                self.tabs.addTab(self.hotplate_test, "Hot Plate")
                self.tabs.addTab(self.serverretainer_test, f"Server Retainer")

            except Exception as e:
                print(f"Error while adding tab: {e}")

    def GetUnitModel(self, workorder_filename):
        try:
            with open(f"Tests\\{workorder_filename}", "r", encoding="utf-8") as file:
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
        try:
            theme_path = resource_path("Themes", f"{self.theme}.qss")

            with open(theme_path, "r", encoding="utf-8") as f:
                qss = f.read()
                app.setStyleSheet(qss)  # use stored reference
        except FileNotFoundError:
            print(f"Theme file Themes/{self.theme}.qss not found.")

    def OnResources(self):
        print("Resources button clicked.")
        try:
            # 1) Make the new window
            self.new_window = QMainWindow()
            self.new_window.setWindowTitle("Resources")
            self.new_window.resize(400, 300)

            # 2) Build the layout and widgets
            layout = QVBoxLayout()

            welcomeLabel = QLabel("COMATS Resources")
            welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            welcomeLabel.setStyleSheet("""
                padding-top: 50px;
                padding-bottom: 50px;
                padding-left: 100px;
                padding-right: 100px;
            """)
            layout.addWidget(welcomeLabel)

            buttonLayout = QVBoxLayout()

            CMMLoader = QComboBox()
            CMMLoader.addItems(["1448-A3 Rev 1 (current)", "1448-A3", "Sorenson DC Power Supply"])
            CMMLoader.setFixedWidth(200)
            buttonLayout.addWidget(CMMLoader, alignment=Qt.AlignmentFlag.AlignCenter)

            CMMLoaderButton = QPushButton("Load CMM")  # no parent here
            CMMLoaderButton.clicked.connect(lambda: self.LoadCMM(CMMLoader))
            buttonLayout.addWidget(CMMLoaderButton, alignment=Qt.AlignmentFlag.AlignCenter)

            PartLocator = QComboBox()
            PartLocator.addItem("UA48-22929209")
            PartLocator.setFixedWidth(200)
            buttonLayout.addWidget(PartLocator, alignment=Qt.AlignmentFlag.AlignCenter)


            PartLocatorButton = QPushButton("Part Locator")  # no parent here
            PartLocatorButton.setFixedWidth(200)
            PartLocatorButton.clicked.connect(self.LoadModel)
            buttonLayout.addWidget(PartLocatorButton, alignment=Qt.AlignmentFlag.AlignCenter)
            buttonLayout.addSpacing(100)

            layout.addLayout(buttonLayout)

            footerLayout = QHBoxLayout()
            back = QPushButton("Settings")
            back.setProperty("class", "small")
            back.setFixedWidth(100)  # 10 was tiny; adjust as needed
            back.setFixedHeight(30)
            # back.clicked.connect(self.ReturnToTest)
            footerLayout.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)

            version = QLabel("V. 2.0.1")
            version.setStyleSheet("font-size:12px;")
            version.setAlignment(Qt.AlignmentFlag.AlignRight)
            footerLayout.addWidget(version)

            layout.addLayout(footerLayout)

            # 3) Attach layout to a container and set it as central widget
            container = QWidget()
            container.setLayout(layout)
            self.new_window.setCentralWidget(container)

            # 4) Finally show the window
            self.new_window.show()

        except Exception as e:
            print(f"Error while opening Resources: {e}")

    def res_path(*parts) -> Path:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
        return base.joinpath(*parts)

    def start_webgl(self):
        self.locator_window = QMainWindow()
        self.locator_window.setWindowTitle("Parts Locator")
        self.locator_window.resize(1200, 800)

        self.appcontainer = QWidget()
        self.locatorlayout = QVBoxLayout(self.appcontainer)
        html = "Unity\\WebGL\\index.html"

        if self.web is None:
            self.web = QWebEngineView(self)
            self.locatorlayout.addWidget(self.web)

        # QUrl.fromLocalFile expects a STRING path (absolute). Use str(html).
        self.web.load(QUrl.fromLocalFile(str(html)))
        self.locator_window.setCentralWidget(self.appcontainer)
        self.locator_window.show()


    def LoadCMM(self, cmmLoader):
        try:
            cmm = cmmLoader.currentText()
            pdf_path = resource_path("Resources", f"{cmm}.pdf")

            if platform.system() == "Darwin":
                subprocess.run(["open", str(pdf_path)])
            elif platform.system() == "Windows":
                os.startfile(str(pdf_path))
            else:
                subprocess.run(["xdg-open", str(pdf_path)])



        except Exception as e:
            print(f"Error returning to main: {e}")

    def LoadModel(self):
        try:
            self.start_webgl()
        except Exception as e:
            print(f"Error loading 3D Model: {e}")



# === Application entry point ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


