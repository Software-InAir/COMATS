from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog, QComboBox
)

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QUrl

from InstrumentWorker import InstrumentWorker

from NumPad import NumericKeypadDialog

import requests
import subprocess
import platform
import os
import sys

from pathlib import Path

class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- WaterLeaks Check

class WaterLeaksTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.waterleaks_results = ""
        self.waterleaks_passed = [False, False, False]
        self.waterleaks_failed = [False, False, False]
        self.waterleaks_completed = False
        self.current_waterleaks_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.waterleakslabellayout = QHBoxLayout()
        self.waterleakstestbuttonlayout = QHBoxLayout()

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
        scroll.setMaximumWidth(1200)
        scroll.setWidgetResizable(True)

        self.waterleakslabel = QLabel(
            "<b>Turn off the ON/OFF switch. <br><br>"
            "   Ensure unit is drained by closing V10 and opening V11. <br><br>"
            "   Turn PG2 on. <br><br>"
            "   Turn on the water supply by closing V11 and opening V10. <br><br>"
            "<i>Verify water pressure is 26 PSIG by checking PG2 while water is flowing.<br><br>"
            "   Water flow rate should be greater than .25 gallons per minute as indicated by FM.</i><br><br>"




        )

        self.waterleakslabel.setTextFormat(Qt.TextFormat.RichText)
        self.waterleakslabel.setWordWrap(True)
        self.waterleakslabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.waterleakslabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.waterleakslabel)


        self.waterleakslabellayout.addWidget(scroll)
        layout.addLayout(self.waterleakslabellayout)
        layout.addLayout(self.waterleakstestbuttonlayout)
        try:
            self.waterleaksbeginbutton = QPushButton("Begin")
            self.waterleaksbeginbutton.setFixedWidth(200)
            self.waterleaksbeginbutton.clicked.connect(self.WaterLeaks)
            self.waterleakstestbuttonlayout.addWidget(self.waterleaksbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

        # -------------------------------------------------------------------- Phase Readings
        self.phaselayout = QHBoxLayout()

        self.resources = QPushButton("Resources")
        self.resources.setFixedWidth(200)
        self.resources.clicked.connect(self.OnResources)
        self.phaselayout.addWidget(self.resources)

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.phaselayout.addSpacerItem(spacer2)

        self.phase1 = QLabel("Phase A:")
        self.phase1.setStyleSheet("""
                                                font: 24px;
                                                """)
        self.phaselayout.addWidget(self.phase1)

        self.phase1reading = QLabel(f"{self.phase1read}")
        self.phase1reading.setStyleSheet("""
                                        font: 24px;
                                        """)
        self.phaselayout.addWidget(self.phase1reading)

        self.phase2 = QLabel("  Phase B:")
        self.phase2.setStyleSheet("""
                                                        font: 24px;
                                                        """)
        self.phaselayout.addWidget(self.phase2)

        self.phase2reading = QLabel(f"{self.phase2read}")
        self.phase2reading.setStyleSheet("""
                                                font: 24px;
                                                """)
        self.phaselayout.addWidget(self.phase2reading)

        self.phase3 = QLabel("  Phase C:")
        self.phase3.setStyleSheet("""
                                                        font: 24px;
                                                        """)
        self.phaselayout.addWidget(self.phase3)

        self.phase3reading = QLabel(f"{self.phase3read}")
        self.phase3reading.setStyleSheet("""
                                                font: 24px;
                                                """)
        self.phaselayout.addWidget(self.phase3reading)

        layout.addLayout(self.phaselayout)

        self.setLayout(layout)

        if self.instrument is not None:
            self.instrument.ch1.connect(self.show_current1)
            self.instrument.ch2.connect(self.show_current2)
            self.instrument.ch3.connect(self.show_current3)

    @pyqtSlot(float)
    def show_current1(self, amps):
        self.phase1.setText(f"Phase 1: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current2(self, amps):
        self.phase2.setText(f"Phase 2: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current3(self, amps):
        self.phase3.setText(f"Phase 3: {amps:.3f} A")

    def WaterLeaks(self):
        try:

            msg1 = QMessageBox()
            # msg1.setIcon(QMessageBox.Icon.Information)

            if self.current_waterleaks_step == 0:
                value1, ok = NumericKeypadDialog.getValue(
                    self,
                    "Water Pressure",
                    "Please enter the water pressure displayed on PG2:",
                    decimals=0,
                    min_value=0.0,
                    max_value=200,
                )
                self.waterleaks_results += f"Water PSIG: {value1} A\n"
                if ok:
                    result_line = f"Water PSIG: {value1}"
                    if value1 >= 25 and value1 <= 27:   #----------------------------------------- Check these limits.
                        result_line += "\tPASS"
                        self.step_status["step1_waterleaks_pressure"] = {
                            "status": "PASS",
                            "value": value1
                        }
                        self.waterleaks_passed[0] = True
                        self.waterleaks_failed[0] = False
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step1_waterleaks_pressure"] = {
                            "status": "FAIL",
                            "value": value1
                        }
                        self.waterleaks_passed[0] = False
                        self.waterleaks_failed[0] = True

                    self.insert_waterleaks_result(result_line)
                    self.post_waterleaks_snapshot()
                    self.updateWaterLeaksStep()
                    self.current_waterleaks_step += 1
                    print(self.current_waterleaks_step)



            # STEP 1 — 4.5 mΩ
            elif self.current_waterleaks_step == 1:
                msg1.setWindowTitle("Check Water Leaks")
                msg1.setText("No water leaks found during inspection")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Water Leaks Inspection Test: "
                    result_line += "\tPASS"
                    self.insert_waterleaks_result(result_line)
                    self.step_status["step2_waterleaks_leak"] = {"status": "PASS"}
                    self.post_waterleaks_snapshot()
                    self.waterleaks_passed[1] = True
                    self.waterleaks_failed[1] = False
                    self.waterleaks_completed = True
                    self.updateWaterLeaksStep()
                    self.current_waterleaks_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Water Leaks Inspection Test: "
                    result_line += "\tFAIL"
                    self.insert_waterleaks_result(result_line)
                    self.step_status["step2_waterleaks_leak"] = {"status": "FAIL"}
                    self.post_waterleaks_snapshot()
                    self.waterleaks_passed[1] = False
                    self.waterleaks_failed[1] = True
                    self.updateWaterLeaksStep()
                    self.current_waterleaks_step += 1


            # Completed
            elif self.waterleaks_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The WaterLeaks test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateWaterLeaksStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateWaterLeaksStep(self):

        if self.waterleaks_passed[0] or self.waterleaks_failed[0]:
            print("Update Water Leaks Step")
            self.waterleakslabel.setText(
            "  <b> The water tank should fill part way (until trapped air in tank is compressed to 26 PSIG) <br><br> "
            "   Water flow should stop completely as indicated by zero on FM. <br><br>"
            "   Residual water flow indicates a water leak.</b> <br><br>"
            "  <i> Visually check the Coffee Maker for leaks too small to cause a residual water flow.</i><br><br>"
            )
            self.waterleaksbeginbutton.setText("Continue")
            self.waterleaksbeginbutton.clicked.disconnect()
            self.waterleaksbeginbutton.clicked.connect(self.WaterLeaks)


        if self.waterleaks_passed[1] or self.waterleaks_failed[1]:
            self.waterleakslabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Water Leaks test has been completed successfully!</b><br><br>"
            )
            self.waterleaksbeginbutton.setText("Results")
            self.waterleaksbeginbutton.clicked.disconnect()
            self.waterleaksbeginbutton.clicked.connect(self.WaterLeaksResults)

            self.waterleaksrestart = QPushButton("Restart", self)
            self.waterleaksrestart.clicked.connect(self.WaterLeaksRestart)
            self.waterleaksrestart.setFixedWidth(200)
            self.waterleakstestbuttonlayout.addWidget(self.waterleaksrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.waterleaksnext = QPushButton("Next", self)
            self.waterleaksnext.clicked.connect(self.WaterLeaksNext)
            self.waterleaksnext.setFixedWidth(200)
            self.waterleakstestbuttonlayout.addWidget(self.waterleaksnext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def WaterLeaksNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetWaterLeaksResults(self):
        return self.waterleaks_results

    def WaterLeaksTestPath(self, path):
        self.test_path = path

    def insert_waterleaks_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Water Leaks Inspection Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Water Leaks section not found.")
                return

            # Step 2: Search after the section header for a matching result line
            for i in range(header_index + 1, len(lines)):
                if lines[i].startswith(">>"):  # Stop at next section
                    break
                if lines[i].startswith(test_id):
                    found_line_index = i
                    break

            if found_line_index != -1:
                lines[found_line_index] = result_line + "\n"
            else:
                lines.insert(header_index + 1, result_line + "\n")

            with open(self.test_path, "w", encoding="utf-8") as file:
                file.writelines(lines)

            print(f"{test_id} written successfully.")

        except Exception as e:
            print(f"Error updating resistance result: {e}")

    def WaterLeaksRestart(self):
        print("Restarting WaterLeaks Test")

    def WaterLeaksResults(self):
        print("Printing WaterLeaks Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[WaterLeaks] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostWaterLeaksResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Low Water: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/waterleaks"
            r = requests.post(url, json=payload, timeout=5)
            print("Water Leaks POST status:", r.status_code)
            print("Water Leaks POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Low Water result: {e}")

    def post_waterleaks_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.waterleaks_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.waterleaks_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.waterleaks_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostWaterLeaksResults(status=overall_status, data=data, notes=notes)


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
            CMMLoader.addItems(["25-33-20"])
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
        html = "C:\\Users\\c.stanley\\Downloads\\COMATS-serverupgrade\\COMATS-serverupgrade\\COMATS-testphase\\Unity\\WebGL\\index.html"

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
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", f"Resources\\{cmm}.pdf"])
            elif platform.system() == "Windows":
                os.startfile(f"Resources\\{cmm}.pdf")  # Windows only
            else:  # Linux and others
                subprocess.run(["xdg-open", f"Resources\\{cmm}.pdf"])



        except Exception as e:
            print(f"Error returnign to main: {e}")

    def LoadModel(self):
        try:
            self.start_webgl()
        except Exception as e:
            print(f"Error loading 3D Model: {e}")