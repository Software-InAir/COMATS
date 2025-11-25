from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot

from InstrumentWorker import InstrumentWorker

from NumPad import NumericKeypadDialog

import requests



class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- RTDCircuit Check

class RTDCircuitTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None

        self.rtdcircuit_results = ""
        self.rtdcircuit_passed = [False, False, False, False]
        self.rtdcircuit_failed = [False, False, False, False]
        self.rtdcircuit_completed = False
        self.current_rtdcircuit_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.rtdcircuitlabellayout = QHBoxLayout()
        self.rtdcircuittestbuttonlayout = QHBoxLayout()

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

        self.rtdcircuitlabel = QLabel(
            "<b>1. With the Beverage Maker connected to the water supply and the red lever on the EDB in the OFF position,"
            " remove the cover from the power module assy and disconnect the RTD assy plug (P4) from the J4"
            " connector on the controller board assy.<br><br>"
            "2. Connect the DMM (set to ohms scale) to the RTD simulator harness (IAS11003A).<br><br>"
            "Rotate the knob until 1430±1 ohms is indicated on the DMM.<br><br>"
            "Change DMM to DC volts then connect harness inline between the controller board assy (J4) and P4.<br><br>"
            "3. Connect the Beverage Maker to the power supply.<br><br>"
            "Set the red lever on the EDB to the ON position.<br><br>"
            "4. Press the power button.<br><br>"
            "<i>This should trip the safety latch.</i><br><br>"
            "<i>(If the safety latch is tripped, there will be no current drawn to the heaters and the power indicator light should go into double-blink mode.)</i><br><br>"
            )

        self.rtdcircuitlabel.setTextFormat(Qt.TextFormat.RichText)
        self.rtdcircuitlabel.setWordWrap(True)
        self.rtdcircuitlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.rtdcircuitlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.rtdcircuitlabel)

        self.rtdcircuitlabellayout.addWidget(scroll)
        layout.addLayout(self.rtdcircuitlabellayout)
        layout.addLayout(self.rtdcircuittestbuttonlayout)
        try:
            self.rtdcircuitbeginbutton = QPushButton("Begin")
            self.rtdcircuitbeginbutton.setFixedWidth(200)
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

        # -------------------------------------------------------------------- Phase Readings
        self.phaselayout = QHBoxLayout()

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

    def RTDCircuit(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_rtdcircuit_step == 0:
                msg1.setWindowTitle("Safety Latch Check")
                msg1.setText("Safety Latch engaged and unit entered double-blink mode.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Test: "
                    result_line += "\tPASS"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step1_rtdcircuit_doubleblink"] = {
                        "status": "PASS",
                    }
                    self.post_rtdcircuit_snapshot()
                    self.rtdcircuit_passed[0] = True
                    self.rtdcircuit_failed[0] = False
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Test: "
                    result_line += "\tFAIL"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step1_rtdcircuit_doubleblink"] = {
                        "status": "FAIL",
                    }
                    self.post_rtdcircuit_snapshot()
                    self.rtdcircuit_passed[0] = False
                    self.rtdcircuit_failed[0] = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_rtdcircuit_step == 1:
                msg1.setWindowTitle("Safety Latch Reset Check")
                msg1.setText("Safety Latch did not engage after resetting and unit did not enter double-blink mode.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Reset Test: "
                    result_line += "\tPASS"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step2_rtdcircuit_safetylatch"] = {
                        "status": "PASS",
                    }
                    self.post_rtdcircuit_snapshot()
                    self.rtdcircuit_passed[1] = True
                    self.rtdcircuit_failed[1] = False
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Reset Test: "
                    result_line += "\tFAIL"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step2_rtdcircuit_safetylatch"] = {
                        "status": "FAIL",
                    }
                    self.post_rtdcircuit_snapshot()
                    self.rtdcircuit_passed[1] = False
                    self.rtdcircuit_failed[1] = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_rtdcircuit_step == 2:
                value, ok = NumericKeypadDialog.getValue(
                    self,
                    "Voltage Check",
                    "Please enter the voltage measurement observed on DMM:",
                    decimals=3,
                    min_value=0.0,
                    max_value=100.0,
                )

                self.rtdcircuit_results += f"Voltage Result: {value} volts\n"
                if ok:
                    result_line = f"Voltage Result: {value} volts"
                    if value <= 2.06:
                        result_line += "\tPASS"
                        self.step_status["step3_rtdcircuit_voltage"] = {
                            "status": "PASS",
                            "value": value
                        }
                        self.post_rtdcircuit_snapshot()
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step3_rtdcircuit_voltage"] = {
                            "status": "FAIL",
                            "value": value
                        }
                        self.post_rtdcircuit_snapshot()
                    self.insert_rtdcircuit_result(result_line)
                    if value <= 2.06:
                        self.rtdcircuit_passed[2] = True
                        self.rtdcircuit_failed[2] = False

                    else:
                        self.rtdcircuit_passed[2] = False
                        self.rtdcircuit_failed[2] = True

                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                return

            # STEP 4 — 5.7 mΩ
            elif self.current_rtdcircuit_step == 3:
                    msg1.setWindowTitle("Safety Latch Check")
                    msg1.setText("Safety Latch not engaged.<br><br>")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        result_line = f"Safety Latch Trip and Double Blink Mode Final Test: "
                        result_line += "\tPASS"
                        self.insert_rtdcircuit_result(result_line)
                        self.step_status["step4_rtdcircuit_safetylatchtrip"] = {
                            "status": "PASS",
                        }
                        self.post_rtdcircuit_snapshot()
                        self.rtdcircuit_passed[3] = True
                        self.rtdcircuit_failed[3] = False
                        self.rtdcircuit_completed = True
                        self.updateRTDCircuitStep()
                        self.current_rtdcircuit_step += 1
                    elif msg1.clickedButton() == fail_button:
                        result_line = f"Safety Latch Trip and Double Blink Mode Final Test: "
                        result_line += "\tPASS"
                        self.insert_rtdcircuit_result(result_line)
                        self.step_status["step4_rtdcircuit_safetylatchtrip"] = {
                            "status": "FAIL",
                        }
                        self.post_rtdcircuit_snapshot()
                        self.rtdcircuit_passed[3] = False
                        self.rtdcircuit_failed[3] = True
                        self.updateRTDCircuitStep()
                        self.current_rtdcircuit_step += 1

            # Completed
            elif self.rtdcircuit_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The RTD Circuit test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateRTDCircuitStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateRTDCircuitStep(self):
        if self.rtdcircuit_passed[0] or self.rtdcircuit_failed[0]:
            self.rtdcircuitlabel.setText(
                "5. Rotate the knob counterclockwise until 2.365±0.003 volts is shown on the DMM.<br><br>"
                "6. Press the power button to turn the Beverage Maker off. <br><br>"
                "7. Reset the safety latch by pressing the manual switch on the back of the power module assy under the grommet.<br><br>"
                "8. Press the power button.<br>"
                "<i>While no current is being drawn by the heaters, the safety latch should not trip and the power indicator light should not go into double-blink mode.</i><br><br>"
                "<i>(Observe for 10 seconds.)</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[1] or self.rtdcircuit_failed[1]:
            self.rtdcircuitlabel.setText(
                "9. Rotate the knob on IAS11003A counterclockwise until DMM reads 2.100 volts.<br><br>"
                "While monitoring the current drawn by the heaters, slowly rotate the knob until no current is drawn by the heaters (readings of ~0 A for each self.phase).<br><br>"
                "<i>The voltage on the DMM should be less than 2.060 volts.</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[2] or self.rtdcircuit_failed[2]:
            self.rtdcircuitlabel.setText(
                "10. Press the POWER button to turn off the Beverage Maker.<br><br>"
                "Set the red lever on the EDB to the OFF position.<br><br>"
                "11. Disconnect the IAS11003A from the controller board assy.<br><br>"
                "Connect the P4 to the controller board assy (J4).<br><br>"
                "12. Put the cover on the power module assy.<br><br>"
                "13. Set the red lever on the EDB to the ON position.<br><br>"
                "14. Press the power button.<br><br> "
                "<i>This should not trip the safety latch.</i><br>"
                "<i>(Make sure the power indicator light does not go into double-blink mode.)</i>"

            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[3] or self.rtdcircuit_failed[3]:
            self.rtdcircuitlabel.setText(
                "<b>Test Complete.<br>"
                "The RTD Circuit Test has been completed successfully!<br><br>"
                "Please press the POWER button to turn off the Beverage Maker.</b><br><br>"
                )

            self.rtdcircuitbeginbutton.setText("Results")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuitResults)

            self.rtdcircuitrestart = QPushButton("Restart", self)
            self.rtdcircuitrestart.clicked.connect(self.RTDCircuitRestart)
            self.rtdcircuitrestart.setFixedWidth(200)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.rtdcircuitnext = QPushButton("Next", self)
            self.rtdcircuitnext.clicked.connect(self.RTDCircuitNext)
            self.rtdcircuitnext.setFixedWidth(200)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitnext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def RTDCircuitNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetRTDCircuitTestResults(self):
        return self.rtdcircuit_results

    def RTDCircuitTestPath(self, path):
        self.test_path = path

    def insert_rtdcircuit_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>RTD Circuit Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("RTD Circuit section not found.")
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

    def RTDCircuitRestart(self):
        print("Restarting RTDCircuit Test")

    def RTDCircuitResults(self):
        print("Printing RTDCircuit Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[RTDCircuit] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostRTDCircuitResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("RTD Circuit: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/rtdcircuit"
            r = requests.post(url, json=payload, timeout=5)
            print("RTD Circuit POST status:", r.status_code)
            print("RTD Circuit POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting RTD Circuit result: {e}")

    def post_rtdcircuit_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.rtdcircuit_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.rtdcircuit_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.rtdcircuit_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostRTDCircuitResults(status=overall_status, data=data, notes=notes)