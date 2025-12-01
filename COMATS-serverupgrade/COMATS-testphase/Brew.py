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


#------------------------------------------------------- Brew Check

class BrewTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None,  parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.brew_results = ""
        self.brew_passed = [False, False, False, False, False, False]
        self.brew_failed = [False, False, False, False, False, False]
        self.brew_completed = False
        self.current_brew_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.brewlabellayout = QHBoxLayout()

        self.brewtestbuttonlayout = QHBoxLayout()

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

        self.brewlabel = QLabel(
            "<b>1. Start this test by making sure the tank is filled with water by closing V11 and opening V10.<br><br>"
            "The water supply pressure should be set to 24 to 29 psig (1.66 to 2.0 barg) as indicated by reading gauge PG2.<br>"
            "The power indicator light should be lit.<br><br>"
            "(NOTE: The WARMER (where applicable) must be on before starting this test.)<br><br>"
            "Put an empty server in the Beverage Maker and lower the brew handle.<br><br>"
            "2. Press the BREW button and observe the flow meter (FM).<br><br>"
            "When flow starts, simultaneously start the provided stopwatch.<br><br>"
            "(NOTE: Brew does not start until the water in the tank is heated.<br>"
            "After the start of flow, there will be an interruption for approximately 10 seconds.<br>"
            "This is normal behaviour and the time is included and accounted for in the brew cycle time.)<br><br>"
            "3. Stop the stopwatch when the flow meter (FM) reaches zero for the second time.</b><br><br>"
            "<i>Elapsed time between when flow begins and ends should be between 2 minutes and 30 seconds and 3 minutes and 35 seconds.</i><br><br>"
            )

        self.brewlabel.setTextFormat(Qt.TextFormat.RichText)
        self.brewlabel.setWordWrap(True)
        self.brewlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.brewlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.brewlabel)


        self.brewlabellayout.addWidget(scroll)
        layout.addLayout(self.brewlabellayout)
        layout.addLayout(self.brewtestbuttonlayout)
        try:
            self.brewbeginbutton = QPushButton("Begin")
            self.brewbeginbutton.setFixedWidth(200)
            self.brewbeginbutton.clicked.connect(self.Brew)
            self.brewtestbuttonlayout.addWidget(self.brewbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def Brew(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_brew_step == 0:
                msg1.setWindowTitle("Elapsed Brew Time")
                msg1.setText("Elapsed Brew time measures 2:30-3:35")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.step_status["step1_brew_time"] = {
                        "status": "PASS",
                    }
                    self.post_brew_snapshot()
                    self.brew_passed[0] = True
                    self.brew_failed[0] = False
                    self.updateBrewStep()
                    self.current_brew_step += 1
                    print(self.current_brew_step)
                elif msg1.clickedButton() == fail_button:
                    self.step_status["step1_brew_time"] = {
                        "status": "FAIL",
                    }
                    self.post_brew_snapshot()
                    self.brew_passed[0] = False
                    self.brew_failed[0] = True
                    self.updateBrewStep()
                    self.current_brew_step += 1
                    print(self.current_brew_step)

            # STEP 2 — 5.12 mΩ
            elif self.current_brew_step == 1:
                msg1.setWindowTitle("Brew Interruption")
                msg1.setText("Lifting brew handle interrupts current brew cycle.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Brew Interruption Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tPASS"
                    self.insert_brew_result(result_line)
                    self.step_status["step2_brew_interrupt"] = {
                        "status": "PASS",
                    }
                    self.post_brew_snapshot()
                    self.brew_passed[1] = True
                    self.brew_failed[1] = False
                    self.updateBrewStep()
                    self.current_brew_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Brew Interruption Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tFAIL"
                    self.insert_brew_result(result_line)
                    self.step_status["step2_brew_interrupt"] = {
                        "status": "FAIL",
                    }
                    self.post_brew_snapshot()
                    self.brew_passed[1] = False
                    self.brew_failed[1] = True
                    self.updateBrewStep()
                    self.current_brew_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_brew_step == 2:
                msg1.setWindowTitle("Brew Continuation")
                msg1.setText("Lowering handle continues current brew cycle.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Brew Continuation Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tPASS"
                    self.step_status["step3_brew_continue"] = {
                        "status": "PASS",
                    }
                    self.post_brew_snapshot()
                    self.insert_brew_result(result_line)
                    self.brew_passed[2] = True
                    self.brew_failed[2] = False
                    self.updateBrewStep()
                    self.current_brew_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Brew Continuation Test: "
                    result_line += "\t\t\t\t\t\t\t\t\t\tFAIL"
                    self.insert_brew_result(result_line)
                    self.step_status["step3_brew_continue"] = {
                        "status": "FAIL",
                    }
                    self.post_brew_snapshot()
                    self.brew_passed[2] = False
                    self.brew_failed[2] = True
                    self.updateBrewStep()
                    self.current_brew_step += 1

                    # STEP 3 — 5.7 mΩ
            elif self.current_brew_step == 3:
                    msg1.setWindowTitle("Consecutive Brews")
                    msg1.setText("Pressing brew after completed cycle does not begin new brew cycle.")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        result_line = f"Consecutive Brew Test: "
                        result_line += "\t\t\t\t\t\t\t\t\t\t\tPASS"
                        self.insert_brew_result(result_line)
                        self.step_status["step4_brew_interrupt"] = {
                            "status": "PASS",
                        }
                        self.post_brew_snapshot()
                        self.brew_passed[3] = True
                        self.brew_failed[3] = False
                        self.updateBrewStep()
                        self.current_brew_step += 1

                    elif msg1.clickedButton() == fail_button:
                        result_line = f"Consecutive Brew Test: "
                        result_line += "\t\t\t\t\t\t\t\t\t\t\tFAIL"
                        self.insert_brew_result(result_line)
                        self.step_status["step4_brew_interrupt"] = {
                            "status": "FAIL",
                        }
                        self.post_brew_snapshot()
                        self.brew_passed[3] = False
                        self.brew_failed[3] = True
                        self.updateBrewStep()
                        self.current_brew_step += 1

                        # STEP 3 — 5.7 mΩ
            elif self.current_brew_step == 4:
                value, ok = NumericKeypadDialog.getValue(
                    self,
                    "Check Temperature",
                    "Please enter the temperature displayed on provided thermometer:",
                    initial=0,
                    min_value=0.0,
                    max_value=300.0,
                    decimals=1
                )
                if ok:
                    if value <= 150:
                        tempsystem = "°C"
                    else:
                        tempsystem = "°F"
                    result_line = f"Brew Temperature Test: {value}{tempsystem} "
                    if tempsystem == "°F":
                        if value >= 175 and value <= 195:
                            result_line += "\t\t\t\t\t\t\t\t\tPASS"
                            self.step_status["step5_brew_temp"] = {
                                "status": "PASS",
                                "value": value,
                            }
                            self.post_brew_snapshot()
                        else:
                            result_line += "\t\t\t\t\t\t\t\t\tFAIL"
                            self.step_status["step5_brew_temp"] = {
                                "status": "FAIL",
                                "value": value,
                            }
                            self.post_brew_snapshot()
                    elif tempsystem == "°C":
                        if value >= 79 and value <= 91:
                            result_line += "\t\t\t\t\t\t\t\t\tPASS"
                            self.step_status["step5_brew_temp"] = {
                                "status": "PASS",
                                "value": value,
                            }
                            self.post_brew_snapshot()
                        else:
                            result_line += "\t\t\t\t\t\t\t\t\tFAIL"
                            self.step_status["step5_brew_temp"] = {
                                "status": "FAIL",
                                "value": value,
                            }
                            self.post_brew_snapshot()
                    self.insert_brew_result(result_line)
                    print(f"User entered: {value} ")
                    self.brew_results += f"Brew Temperature Test Result: {value}\n"
                    self.brew_passed[4] = True
                    self.brew_failed[4] = False
                    self.current_brew_step += 1
                    self.updateBrewStep()

                        # STEP 3 — 5.7 mΩ
            elif self.current_brew_step == 5:
                        msg1.setWindowTitle("Power Indicator Light")
                        msg1.setText("Power indicator light turns on briefly and deactivates.")
                        pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                        fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                        msg1.exec()

                        if msg1.clickedButton() == pass_button:
                            result_line = f"Power Indicator Test: "
                            result_line += "\t\t\t\t\t\t\t\t\t\t\tPASS"
                            self.insert_brew_result(result_line)
                            self.step_status["step6_brew_indicator"] = {
                                "status": "PASS",
                            }
                            self.post_brew_snapshot()
                            self.brew_passed[5] = True
                            self.brew_failed[5] = False
                            self.brew_completed = True
                            self.updateBrewStep()
                            self.current_brew_step += 1
                        elif msg1.clickedButton() == fail_button:
                            result_line = f"Power Indicator Test: "
                            result_line += "\t\t\t\t\t\t\t\t\t\t\tFAIL"
                            self.insert_brew_result(result_line)
                            self.step_status["step6_brew_indicator"] = {
                                "status": "PASS",
                            }
                            self.post_brew_snapshot()
                            self.brew_passed[5] = False
                            self.brew_failed[5] = True
                            self.updateBrewStep()
                            self.current_brew_step += 1

            # Completed
            elif self.brew_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Brew test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateBrewStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateBrewStep(self):
        if self.brew_passed[0] or self.brew_failed[0]:
            self.brewlabel.setText(
                "<b>4. Lift the brew handle, remove, empty, and install server in the Beverage Maker.<br><br>"
                "5. With the brew button light off, press the brew button to start a second brew.<br><br>"
                "6. Lift brew handle after the normal 10 second flow interruption.</b><br><br>"
                "<i>Lifting the brew handle should interrupt the brew cycle, as shown by the flow meter reaching zero.</i><br><br>"
                )

            self.brewbeginbutton.setText("Continue")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.Brew)

        if self.brew_passed[1] or self.brew_failed[1]:
            self.brewlabel.setText(
                "<b>7. Lower the brew handle.<br><br>"
                "<i>This should continue the current brew cycle.</i><br><br>"
                )

            self.brewbeginbutton.setText("Continue")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.Brew)

        if self.brew_passed[2] or self.brew_failed[2]:
            self.brewlabel.setText(
                "8. When the brew indicator light goes off, press the brew button again<br><br>"
                "<i>Another brew cycle should not begin.</i><br><br>"
                )

            self.brewbeginbutton.setText("Continue")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.Brew)

        if self.brew_passed[3] or self.brew_failed[3]:
            self.brewlabel.setText(
                "<b>9. Lift the brew handle and measure the temperature of the liquid in the server by using the provided digital thermometer.<br><br>"
                "<i>It should measure between 175° F (79° C) and 195° F (91° C).</i><br><br>"
                )

            self.brewbeginbutton.setText("Continue")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.Brew)

        if self.brew_passed[4] or self.brew_failed[4]:
            self.brewlabel.setText(
                "<b>The server should be full.<br><br>"
                "10. Place the full server in the Beverage Maker and lower the brew handle.<br><br>"
                "11. Press the brew button.<br><br>"
                "<i>The brew indicator light should come on for a short time and then proceed to turn off.</i><br><br>"
                "<i>(The full server should be detected by the backup liquid level sensor for the server.)</i><br><br>"
                )

            self.brewbeginbutton.setText("Continue")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.Brew)

        if self.brew_passed[5] or self.brew_failed[5]:
            self.brewlabel.setText(
                    "<b>Test Complete.<br><br>"
                    "The Brew Test has been completed successfully.<br><br>"
                    "Please lift the brew handle, remove, empty, and install the server back into the Beverage Maker. After the server is inserted, lower the brew handle.<br><br>."
                    )

            self.brewbeginbutton.setText("Results")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.BrewResults)

            self.brewrestart = QPushButton("Restart", self)
            self.brewrestart.clicked.connect(self.BrewRestart)
            self.brewrestart.setFixedWidth(200)
            self.brewtestbuttonlayout.addWidget(self.brewrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.brewnext = QPushButton("Next", self)
            self.brewnext.clicked.connect(self.BrewNext)
            self.brewnext.setFixedWidth(200)
            self.brewtestbuttonlayout.addWidget(self.brewnext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def BrewNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetBrewResults(self):
        return self.brew_results

    def BrewTestPath(self, path):
        self.test_path = path

    def insert_brew_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Brew Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Brew section not found.")
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

    def BrewRestart(self):
        print("Restarting Brew Test")

    def BrewResults(self):
        print("Printing Brew Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[Brew] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostBrewResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Brew: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/brew"
            r = requests.post(url, json=payload, timeout=5)
            print("Brew POST status:", r.status_code)
            print("Brew POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Brew result: {e}")

    def post_brew_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.brew_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.brew_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.brew_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostBrewResults(status=overall_status, data=data, notes=notes)

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
            CMMLoader.addItems(["25-30-02", "25-30-03", "25-30-50", "25-33-20", "25-33-21", "25-33-32"])
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