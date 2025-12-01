from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy,
                             QPushButton, QScrollArea, QMessageBox, QInputDialog, QTabWidget, QMainWindow, QComboBox)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QUrl

from InstrumentWorker import InstrumentWorker

import requests
import subprocess
import platform
import os
import sys

from pathlib import Path

#------------------------------------------------------- LowWater Check

class LowWaterTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.lowwater_results = ""
        self.lowwater_passed = [False, False, False, False]
        self.lowwater_failed = [False, False, False, False]
        self.lowwater_completed = False
        self.current_lowwater_step = 0

        self.step_status = {}


        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.lowwaterlabellayout = QHBoxLayout()

        self.lowwatertestbuttonlayout = QHBoxLayout()

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

        self.lowwaterlabel = QLabel(
            "<b>    Make sure that the Coffee Maker water tank is empty.<br><br>"
            "       Verify V10 is closed, open V11 to ensure water lines are drained.<br><br>"
            "       Ensure EDB is in the OFF position.<br><br>"
            "       Connect unit to power and water supplies.<br><br>"
            "       Set EDB to the on position.<br><br>"
            "       Press ON/OFF switch.</b><br><br>"
            "       <i>ON/OFF and LOW WATER lamps should come on.</i><br><br>"
            )

        self.lowwaterlabel.setTextFormat(Qt.TextFormat.RichText)
        self.lowwaterlabel.setWordWrap(True)
        self.lowwaterlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.lowwaterlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.lowwaterlabel)


        self.lowwaterlabellayout.addWidget(scroll)
        layout.addLayout(self.lowwaterlabellayout)
        layout.addLayout(self.lowwatertestbuttonlayout)
        try:
            self.lowwaterbeginbutton = QPushButton("Begin")
            self.lowwaterbeginbutton.setFixedWidth(200)
            self.lowwaterbeginbutton.clicked.connect(self.LowWater)
            self.lowwatertestbuttonlayout.addWidget(self.lowwaterbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def LowWater(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_lowwater_step == 0:
                msg1.setWindowTitle("Lamp Tests")
                msg1.setText("ON/OFF and Low Water Lamps activated")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.lowwater_passed[0] = True
                    self.lowwater_failed[0] = False
                    result_line = f"ON/OFF and Low Water Indicator Light Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tPASS"
                    self.insert_lowwater_result(result_line)
                    self.step_status["step1_lowwater_indicatorlamps"] = "PASS"
                    self.updateLowWaterStep()
                    self.current_lowwater_step += 1
                    print(self.current_lowwater_step)
                elif msg1.clickedButton() == fail_button:
                    self.lowwater_passed[0] = False
                    self.lowwater_failed[0] = True
                    result_line = f"ON/OFF and Low Water Indicator Light Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tFAIL"
                    self.insert_lowwater_result(result_line)
                    self.step_status["step1_lowwater_indicatorlamps"] = "FAIL"
                    self.current_lowwater_step += 1
                    self.updateLowWaterStep()

                    print(self.current_lowwater_step)

            # STEP 2 — 5.12 mΩ
            elif self.current_lowwater_step == 1:
                msg1.setWindowTitle("Low Water Deactivation")
                msg1.setText("Low Water Indicator Light Deactivates when tank reaches capacity.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Low Water Indicator Light Deactivate Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tPASS"
                    self.insert_lowwater_result(result_line)
                    self.step_status["step2_lowwater_indicatorlampsoff"] = \
                        {"status": "PASS"}
                    self.post_lowwater_snapshot()
                    self.lowwater_passed[1] = True
                    self.lowwater_failed[1] = False
                    self.current_lowwater_step += 1
                    self.updateLowWaterStep()

                elif msg1.clickedButton() == fail_button:
                    result_line = f"Low Water Indicator Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tFAIL"
                    self.insert_lowwater_result(result_line)
                    self.step_status["step2_lowwater_indicatorlampsoff"] = \
                        {"status": "FAIL"}
                    self.post_lowwater_snapshot()
                    self.lowwater_passed[1] = False
                    self.lowwater_failed[1] = True
                    self.current_lowwater_step += 1
                    self.updateLowWaterStep()


            # STEP 3 — 5.7 mΩ
            elif self.current_lowwater_step == 2:
                value, ok = QInputDialog.getDouble(
                    self,
                    "Check Phase A",
                    "Please enter the amperage displayed on self.phase readings:",
                    value=0.0,
                    min=0.0,
                    max=300.0,
                    decimals=1
                )

                result_line = f"Phase A Amperage Test: {value}"

                if ok:
                    if value <= 0.1:
                        result_line += "\t\t\t\t\t\t\t\t\t\t\t\tPASS"
                        self.lowwater_passed[2] = True
                        self.lowwater_failed[2] = False
                        self.step_status["step3_lowwater_phasea"] = {
                            "status": "PASS",
                            "value": value
                        }
                        self.post_lowwater_snapshot()
                    else:
                        result_line += "\t\t\t\t\t\t\t\t\t\tFAIL"
                        self.lowwater_passed[2] = False
                        self.lowwater_failed[2] = True
                        self.step_status["step3_lowwater_phasea"] = {
                            "status": "FAIL",
                            "value": value
                        }
                        self.post_lowwater_snapshot()
                    self.insert_lowwater_result(result_line)
                    self.post_lowwater_snapshot()

                    print(f"User entered: {value}")
                    self.lowwater_results += f"Phase A: {value} A\n"
                    self.current_lowwater_step += 1
                    self.updateLowWaterStep()


            elif self.current_lowwater_step == 3:
                value, ok = QInputDialog.getDouble(
                    self,
                    "Check Phase B",
                    "Please enter the amperage displayed on self.phase readings:",
                    value=0.0,
                    min=0.0,
                    max=300.0,
                    decimals=1
                )

                result_line = f"Phase B Amperage Test: {value}"

                if ok:
                    if value <= 0.1:
                        result_line += "\t\t\t\t\t\t\t\t\t\t\t\tPASS"
                        self.lowwater_passed[3] = True
                        self.lowwater_failed[3] = False
                        self.step_status["step4_lowwater_phaseb"] = {
                            "status": "PASS",
                            "value": value
                        }
                        self.post_lowwater_snapshot()
                    else:
                        result_line += "\t\t\t\t\t\t\t\t\t\tFAIL"
                        self.lowwater_passed[3] = False
                        self.lowwater_failed[3] = True
                        self.step_status["step4_lowwater_phaseb"] = {
                            "status": "FAIL",
                            "value": value
                        }
                        self.post_lowwater_snapshot()

                    self.insert_lowwater_result(result_line)
                    self.post_lowwater_snapshot()

                    print(f"User entered: {value}")
                    self.lowwater_results += f"Phase B: {value} A\n"
                    self.current_lowwater_step += 1
                    self.lowwater_completed = True
                    self.updateLowWaterStep()



        except Exception as e:
            print(f"Error: {e}")

    def updateLowWaterStep(self):
        if self.lowwater_passed[0] or self.lowwater_failed[0]:
            self.lowwaterlabel.setText(
                "<b>Close V11 and open V10.\n Water tank should finish filling.</b><br><br>"
                "<i>LOW WATER lamp should turn off once tank is full as indicated by zero on flow meter (FM).</i><br><br>"
                )

            self.lowwaterbeginbutton.setText("Continue")
            self.lowwaterbeginbutton.clicked.disconnect()
            self.lowwaterbeginbutton.clicked.connect(self.LowWater)

        if self.lowwater_passed[1] or self.lowwater_failed[1]:
            self.lowwaterlabel.setText(
                "<i>Phase A line current should be less than 0.1 amps.<br>"
                "Phases B and C should be zero.</i><br><br>"
            )
            self.lowwaterbeginbutton.setText("Continue")
            self.lowwaterbeginbutton.clicked.disconnect()
            self.lowwaterbeginbutton.clicked.connect(self.LowWater)


        if self.lowwater_completed:
            self.lowwaterlabel.setText(
                    "<b>Test Complete.<br><br>"
                    "The Low Water Test has been completed successfully.<br><br>"
                    )

            self.lowwaterbeginbutton.setText("Results")
            self.lowwaterbeginbutton.clicked.disconnect()
            self.lowwaterbeginbutton.clicked.connect(self.LowWaterResults)

            self.lowwaterrestart = QPushButton("Restart", self)
            self.lowwaterrestart.clicked.connect(self.LowWaterRestart)
            self.lowwaterrestart.setFixedWidth(200)
            self.lowwatertestbuttonlayout.addWidget(self.lowwaterrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.lowwaternext = QPushButton("Next", self)
            self.lowwaternext.clicked.connect(self.LowWaterNext)
            self.lowwaternext.setFixedWidth(200)
            self.lowwatertestbuttonlayout.addWidget(self.lowwaternext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def LowWaterNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetLowWaterResults(self):
        return self.lowwater_results

    def LowWaterTestPath(self, path):
        self.test_path = path

    def insert_lowwater_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Low Water Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Low Water section not found.")
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

    def LowWaterRestart(self):
        print("Restarting LowWater Test")

    def LowWaterResults(self):
        print("Printing LowWater Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[LowWater] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostLowWaterResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Low Water: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/lowwater"
            r = requests.post(url, json=payload, timeout=5)
            print("Low Water POST status:", r.status_code)
            print("Low Water POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Low Water result: {e}")

    def post_lowwater_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.lowwater_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.lowwater_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.lowwater_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostLowWaterResults(status=overall_status, data=data, notes=notes)


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
