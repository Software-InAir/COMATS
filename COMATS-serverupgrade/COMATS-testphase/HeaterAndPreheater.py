from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal

from InstrumentWorker import InstrumentWorker

import requests



class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- HeaterAndPreheater Check

class HeaterAndPreheaterTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker

        self.test_id: int | None = None
        self.api_base_url: str | None = None

        self.heaterandpreheater_results = ""
        self.heaterandpreheater_passed = [False, False, False]
        self.heaterandpreheater_failed = [False, False, False]
        self.heaterandpreheater_completed = False
        self.current_heaterandpreheater_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.heaterandpreheaterlayout = QHBoxLayout()
        heaterandpreheatertestbuttonlayout = QHBoxLayout()

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

        self.heaterandpreheaterlabel = QLabel(
            "<b>1. With the Beverage Maker tank filled with water, be prepared to time preheating before pressing the power button.<br><br>"
            "2. Press the POWER button and start the provided stopwatch.<br><br>"
            "Turn on warmer (if applicable).<b><br><br>"
            "<i>Make sure the amperes for the self.phases are measured as follows:</br>"
            "Phase A: 8.1 +0.6/-0.9 amperes<br>"
            "Phase B:7.8 +0.4/-0.7 amperes<br>"
            "Phase C:7.8 +0.4/-0.7 amperes</i><br><br>"
            )

        self.heaterandpreheaterlabel.setTextFormat(Qt.TextFormat.RichText)
        self.heaterandpreheaterlabel.setWordWrap(True)
        self.heaterandpreheaterlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.heaterandpreheaterlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.heaterandpreheaterlabel)

        self.heaterandpreheaterlayout.addWidget(scroll)
        layout.addLayout(self.heaterandpreheaterlayout)
        layout.addLayout(heaterandpreheatertestbuttonlayout)
        try:
            self.heaterandpreheaterbeginbutton = QPushButton("Begin")
            self.heaterandpreheaterbeginbutton.setFixedWidth(200)
            self.heaterandpreheaterbeginbutton.clicked.connect(self.HeaterAndPreheater)
            heaterandpreheatertestbuttonlayout.addWidget(self.heaterandpreheaterbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

        # -------------------------------------------------------------------- Phase Readings
        self.phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.phaselayout.addSpacerItem(spacer2)

        self.phase1 = QLabel("Phase 1:")
        self.phaselayout.addWidget(self.phase1)

        self.phase1reading = QLabel(f"{self.phase1read}")
        self.phaselayout.addWidget(self.phase1reading)

        self.phase2 = QLabel("Phase 2:")
        self.phaselayout.addWidget(self.phase2)

        self.phase2reading = QLabel(f"{self.phase2read}")
        self.phaselayout.addWidget(self.phase2reading)

        self.phase3 = QLabel("Phase 3")
        self.phaselayout.addWidget(self.phase3)

        self.phase3reading = QLabel(f"{self.phase3read}")
        self.phaselayout.addWidget(self.phase3reading)

        layout.addLayout(self.phaselayout)

        self.setLayout(layout)
        #tabs.addTab(heaterandpreheater, f"HeaterAndPreheater")


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

    def HeaterAndPreheater(self):
        try:
            msg1 = QMessageBox()
            # msg1.setIcon(QMessageBox.Icon.Information)

            if self.current_heaterandpreheater_step == 0:
                value1, ok = QInputDialog.getDouble(
                    self,
                    "Phase A Check",
                    "Please enter the current measurement for Phase A in amperes:",
                    decimals=1,
                    min=0.0,
                    max=100.0,
                    step=0.01
                )
                self.heaterandpreheater_results += f"Phase A current: {value1} A\n"
                if ok:
                    result_line = f"Phase A current: {value1} A"
                    if value1 >= 7.2 and value1 <= 8.7:
                        result_line += "\tPASS"
                        self.step_status["step1_heaterandpreheater_phasea"] = {
                            "status": "PASS",
                            "value": value1
                        }
                        self.post_heaterandpreheater_snapshot()
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step1_heaterandpreheater_phasea"] = {
                            "status": "FAIL",
                            "value": value1
                        }
                        self.post_heaterandpreheater_snapshot()
                    self.insert_heaterandpreheater_result(result_line)

                    value2, ok = QInputDialog.getDouble(
                        self,
                        "Phase B Check",
                        "Please enter the current measurement for Phase B in amperes:",
                        decimals=1,
                        min=0.0,
                        max=100.0,
                        step=0.01
                    )
                    self.heaterandpreheater_results += f"Phase B current: {value2} A\n"
                    if ok:
                        result_line = f"Phase B current: {value2} A"
                        if value2 >= 7.1 and value2 <= 8.2:
                            result_line += "\tPASS"
                            self.step_status["step2_heaterandpreheater_phaseb"] = {
                                "status": "PASS",
                                "value": value1
                            }
                            self.post_heaterandpreheater_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step2_heaterandpreheater_phaseb"] = {
                                "status": "FAIL",
                                "value": value1
                            }
                            self.post_heaterandpreheater_snapshot()
                        self.insert_heaterandpreheater_result(result_line)

                        value3, ok = QInputDialog.getDouble(
                            self,
                            "Phase C Check",
                            "Please enter the current measurement for Phase C in amperes:",
                            decimals=1,
                            min=0.0,
                            max=100.0,
                            step=0.01
                        )
                        self.heaterandpreheater_results += f"Phase C current: {value3} A\n"
                        if ok:
                            self.current_heaterandpreheater_step += 1
                            print(self.current_heaterandpreheater_step)

                            result_line = f"Phase C current: {value3} A"
                            if value3 >= 7.1 and value3 <= 8.2:
                                result_line += "\tPASS"
                                self.step_status["step3_heaterandpreheater_phasec"] = {
                                    "status": "PASS",
                                    "value": value1
                                }
                                self.post_heaterandpreheater_snapshot()
                            else:
                                result_line += "\tFAIL"
                                self.step_status["step3_heaterandpreheater_phasec"] = {
                                    "status": "FAIL",
                                    "value": value1
                                }
                                self.post_heaterandpreheater_snapshot()
                            self.insert_heaterandpreheater_result(result_line)
                            if value3 >= 7.1 and value3 <= 8.2 and value2 >= 7.1 and value2 <= 8.2 and value1 >= 7.2 and value1 <= 8.7 :
                                self.heaterandpreheater_passed[0] = True
                                self.heaterandpreheater_failed[0] = False
                                self.heaterandpreheater_completed = True
                            else:
                                self.heaterandpreheater_passed[0] = False
                                self.heaterandpreheater_failed[0] = True
                            self.updateHeaterAndPreheaterStep()



                        return



            # STEP 2 — 5.12 mΩ
            elif self.current_heaterandpreheater_step == 1:
                msg1.setWindowTitle("Preheat Time Measurement")
                msg1.setText("The elapsed time measured under 3 minutes and 30 seconds<br><br>")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Elapsed Time Test: "
                    result_line += "\tPASS"
                    self.insert_heaterandpreheater_result(result_line)
                    self.step_status["step4_heaterandpreheater_time"] = {
                        "status": "PASS",
                    }
                    self.post_heaterandpreheater_snapshot()
                    self.heaterandpreheater_passed[1] = True
                    self.heaterandpreheater_failed[1] = False
                    self.heaterandpreheater_completed = True
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Elapsed Time Test: "
                    result_line += "\tFAIL"
                    self.insert_heaterandpreheater_result(result_line)
                    self.step_status["step4_heaterandpreheater_time"] = {
                        "status": "FAIL",
                    }
                    self.post_heaterandpreheater_snapshot()
                    self.heaterandpreheater_passed[1] = False
                    self.heaterandpreheater_failed[1] = True
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1


            # Completed
            elif self.heaterandpreheater_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Heater And Preheater test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateHeaterAndPreheaterStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHeaterAndPreheaterStep(self):
        if self.heaterandpreheater_passed[0] or self.heaterandpreheater_failed[0]:
            self.heaterandpreheaterlabel.setText(
                "<b>4. Stop the stopwatch when the current on Phase B goes to zero.</b><br><br>"
                "<i>The elapsed time should be 3 minutes and 30 seconds at maximum (The measured time must begin from room temperature contents.<br><br>"
                "(NOTE: A small amount of water may come out of pressure relief valve drain line as the tank completes preheating. This is normal behaviour.)"
            )

            self.heaterandpreheaterbeginbutton.setText("Continue")
            self.heaterandpreheaterbeginbutton.clicked.disconnect()
            self.heaterandpreheaterbeginbutton.clicked.connect(self.HeaterAndPreheater)


        if self.heaterandpreheater_passed[1] or self.heaterandpreheater_failed[1]:
            self.heaterandpreheaterlabel.setText(
                "<b>Test Completed.<br><br>"
                "<bThe >Heater And Preheater Test has been completed successfully!</b><br><br>"
            )
            self.heaterandpreheaterbeginbutton.setText("Results")
            self.heaterandpreheaterbeginbutton.clicked.disconnect()
            self.heaterandpreheaterbeginbutton.clicked.connect(self.HeaterAndPreheaterResults)

            self.heaterandpreheaterrestart = QPushButton("Restart", self)
            self.heaterandpreheaterrestart.clicked.connect(self.HeaterAndPreheaterRestart)
            self.heaterandpreheaterrestart.setFixedWidth(200)
            self.heaterandpreheatertestbuttonlayout.addWidget(self.heaterandpreheaterrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetHeaterAndPreheaterResults(self):
        return self.heaterandpreheater_results

    def HeaterAndPreheaterTestPath(self, path):
        self.test_path = path

    def insert_heaterandpreheater_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Tank Heater and Preheater Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Tank Heater and Preheater Test section not found.")
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

    def HeaterAndPreheaterRestart(self):
        print("Restarting HeaterAndPreheater Test")

    def HeaterAndPreheaterResults(self):
        print("Printing HeaterAndPreheater Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[HeaterAndPreheater] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostHeaterAndPreheaterResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Heater and Preheater: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/heaterandpreheater"
            r = requests.post(url, json=payload, timeout=5)
            print("Heater and Preheater POST status:", r.status_code)
            print("Heater and Preheater POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Heater and Preheater result: {e}")

    def post_heaterandpreheater_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.heaterandpreheater_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.heaterandpreheater_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.heaterandpreheater_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostHeaterAndPreheaterResults(status=overall_status, data=data, notes=notes)
