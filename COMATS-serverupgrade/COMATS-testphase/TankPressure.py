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



#------------------------------------------------------- TankPressure Check

class TankPressureTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker

        self.test_id: int | None = None
        self.api_base_url: str | None = None

        self.tankpressure_results = ""
        self.tankpressure_passed = [False, False, False]
        self.tankpressure_failed = [False, False, False]
        self.tankpressure_completed = False
        self.current_tankpressure_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.tankpressurelabellayout = QHBoxLayout()
        self.tankpressuretestbuttonlayout = QHBoxLayout()

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

        self.tankpressurelabel = QLabel(
            "<b>Remove plastic drain tube from clip behind server.<br><br>"
            "Use 11/16 wrench to remove pressure relief valve.<br><br>"
            "Use a 7/16 wrench to secure 1/8 inch NPT plug wrapped with teflon tape.<br><br>"
            "1. Replace the pressure relief valve with a 1/8 inch NPT plug prior to " 
            "testing.<br><br>"
            "Close V10 then turn V8 vertical. <br><br>"
            "2. Connect the Beverage Maker to water supply and then open V10.<br><br>"
            "3. Let tank fill with water. Flow meter will go to zero when tank is full.<br><br>" 
            "4. Adjust water pressure by rotating V7 clockwise until PG2 reads 130 psig (8.96 barg).<br><br>"
            "Hold for a minimum of 5 minutes.<br><br>"
            "Inspect tank for leaks.<br><br>"
            "<i>No leaks are allowed.</i><br><br>"
        )

        self.tankpressurelabel.setTextFormat(Qt.TextFormat.RichText)
        self.tankpressurelabel.setWordWrap(True)
        self.tankpressurelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.tankpressurelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.tankpressurelabel)

        self.tankpressurelabellayout.addWidget(scroll)
        layout.addLayout(self.tankpressurelabellayout)
        layout.addLayout(self.tankpressuretestbuttonlayout)
        try:
            self.tankpressurebeginbutton = QPushButton("Begin")
            self.tankpressurebeginbutton.setFixedWidth(200)
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)
            self.tankpressuretestbuttonlayout.addWidget(self.tankpressurebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(tankpressure, f"TankPressure")

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

    def TankPressure(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_tankpressure_step == 0:
                msg1.setWindowTitle("Check Tank")
                msg1.setText("No tank leaks found.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Leak Check Test: "
                    result_line += "\tPASS"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step1_tankpressure_leak"] = {
                        "status": "PASS",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[0] = True
                    self.tankpressure_failed[0] = False
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Leak Check Test: "
                    result_line += "\tFAIL"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step1_tankpressure_leak"] = {
                        "status": "FAIL",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[0] = False
                    self.tankpressure_failed[0] = True
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1

            elif self.current_tankpressure_step == 1:
                msg1.setWindowTitle("Check Vent Valve")
                msg1.setText("Vent Valve operates as instructed.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Vent Valve Test: "
                    result_line += "\tPASS"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step2_tankpressure_ventvalve"] = {
                        "status": "PASS",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[1] = True
                    self.tankpressure_failed[1] = False
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Vent Valve Test: "
                    result_line += "\tFAIL"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step2_tankpressure_ventvalve"] = {
                        "status": "FAIL",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[1] = False
                    self.tankpressure_failed[1] = True
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1

            # STEP 2 — 5.12 mΩ
            if self.current_tankpressure_step == 2:
                value, ok = QInputDialog.getDouble(
                    self,
                    "Check Pressure",
                    "Please enter the pressure displayed on PG:",
                    decimals=2,
                    min=0.0,
                    max=100.0,
                    step=0.01
                )

                if ok:

                    result_line = f"Tank Pressure Test {self.current_tankpressure_step + 1}: {value} PSI "
                    if value < 30:
                        result_line += "\tPASS"
                        self.step_status["step3_tankpressure_pressure"] = {
                            "status": "PASS",
                            "value": value
                        }
                        self.post_tankpressure_snapshot()
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step3_tankpressure_pressure"] = {
                            "status": "FAIL",
                            "value": value
                        }
                        self.post_tankpressure_snapshot()

                    self.insert_tankpressure_result(result_line)
                    print(f"User entered: {value} PSI")
                    self.tankpressure_results += f"Test {self.current_tankpressure_step + 1} Result: {value}\n"
                    self.tankpressure_passed[0] = True
                    self.tankpressure_failed[0] = False
                    self.current_tankpressure_step += 1
                    self.updateTankPressureStep()



            # Completed
            elif self.tankpressure_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The TankPressure test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateTankPressureStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateTankPressureStep(self):
        if self.tankpressure_passed[0] or self.tankpressure_failed[0]:
            self.tankpressurelabel.setText(
                "Rotate V7 counterclockwise until PG2 reads below 70 psi.<br><br>"
                "Open V9 periodically to verify pressure is below 70 psi.<br><br>"
                "Close V10.<br><br>"
                "5. Release pressure by opening V11 then remove plug.<br><br>"
                "6. Put pressure relief valve back into the tank using thread seal tape.<br>"
                "Insert plastic drain tube back into original place.<br>"
                "Tighten with 11/16 wrench.<br>"
                "Close V11 and open V10.7.<br><br>"
                "Gradually increase the water pressure to the tank.<br>"
                "Slowly rotate V7 clockwise while watching PG2.<br><br>"
                "<i>The relief valve should remain closed at pressures below 75 psig (5.17 barg).</i><br><br>"
                "Continue to increase pressure ensuring the valve is fully open prior to or at 100 psig (6.89 barg).<br><br>"
                "8. Disconnect water supply by turning V10 off and drain the Beverage Maker by opening V11.<br><br>"
                "<i>Ensure that vent valve operates correctly as described.</i><br><br>"
            )

            self.tankpressurebeginbutton.setText("Continue")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)


        if self.tankpressure_passed[1] or self.tankpressure_failed[1]:
            self.tankpressurelabel.setText(
                "Turn V7 counterclockwise to return pressure to 50 psi while periodically opening V9 to verify.<br><br>"
                "Turn V8 horizontal.<br>"
                "Open V9<br><br>"
                "<i>Verify pressure is less than 30 on PG2.</i><br><br>"
            )
            self.tankpressurebeginbutton.setText("Continue")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)

        if self.tankpressure_passed[1] or self.tankpressure_failed[1]:
            self.tankpressurelabel.setText(
                    "Test Complete.<br><br>"
                    "Tank Pressure Test has been completed successfully!<br>"
                )
            self.tankpressurebeginbutton.setText("Results")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressureResults)



            self.tankpressurerestart = QPushButton("Restart", self)
            self.tankpressurerestart.clicked.connect(self.TankPressureRestart)
            self.tankpressurerestart.setFixedWidth(200)
            self.tankpressuretestbuttonlayout.addWidget(self.tankpressurerestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetTankPressureResults(self):
        return self.tankpressure_results

    def TankPressureTestPath(self, path):
        self.test_path = path

    def insert_tankpressure_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Tank Pressure Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Tank Pressure section not found.")
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
            print(f"Error updating tank pressure result: {e}")

    def TankPressureRestart(self):
        print("Restarting TankPressure Test")

    def TankPressureResults(self):
        print("Printing TankPressure Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[TankPressure] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostTankPressureResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Tank Pressure: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/tankpressure"
            r = requests.post(url, json=payload, timeout=5)
            print("Tank Pressure POST status:", r.status_code)
            print("Tank Pressure POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Tank Pressure result: {e}")

    def post_tankpressure_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.tankpressure_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.tankpressure_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.tankpressure_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostTankPressureResults(status=overall_status, data=data, notes=notes)