from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
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



#------------------------------------------------------- PowerAndLowLight Check

class PowerAndLowLightTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None

        self.powerandlowlight_results = ""
        self.powerandlowlight_passed = [False, False, False, False, False]
        self.powerandlowlight_failed = [False, False, False, False, False]
        self.powerandlowlight_completed = False
        self.current_powerandlowlight_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.powerandlowlightlayout = QHBoxLayout()

        self.powerandlowlighttestbuttonlayout = QHBoxLayout()

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

        self.powerandlowlightlabel = QLabel(
            "1. Connect the Beverage Maker to the power supply.<br><br>"
            "<i>Ensure EDB is in the ON position.</i><br><br>"
            "2. If connected, disconnect the water supply from the Beverage Maker by closing V10 and opening V11.<br><br>"
            "3. Press the power button.<br><br>"
            "4.<i>>Both the power and low water indicators should be lit without the heaters activating "
            "<br>(as indicated by ~0 A readings for each self.phase of the power supply).</i><br><br>"
        )

        self.powerandlowlightlabel.setTextFormat(Qt.TextFormat.RichText)
        self.powerandlowlightlabel.setWordWrap(True)
        self.powerandlowlightlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.powerandlowlightlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.powerandlowlightlabel)


        self.powerandlowlightlayout.addWidget(scroll)
        layout.addLayout(self.powerandlowlightlayout)
        layout.addLayout(self.powerandlowlighttestbuttonlayout)
        try:
            self.powerandlowlightbeginbutton = QPushButton("Begin")
            self.powerandlowlightbeginbutton.setFixedWidth(200)
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)
            self.powerandlowlighttestbuttonlayout.addWidget(self.powerandlowlightbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def PowerAndLowLight(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_powerandlowlight_step == 0:
                msg1.setWindowTitle("Power and Low Indicator Lights")
                msg1.setText("<i>Power and Low Indicator Lights activated.</i><br><br>")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Power and Low Indicator Light activated: "
                    result_line += "\tPASS"
                    self.insert_powerandlowlight_result(result_line)
                    self.step_status["step1_powerandlowlight_indicatorsactive"] = {
                        "status": "PASS",
                    }
                    self.post_powerandlowlight_snapshot()
                    self.powerandlowlight_passed[0] = True
                    self.powerandlowlight_failed[0] = False
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Power and Low Indicator Lights activated: "
                    result_line += "\tFAIL"
                    self.insert_powerandlowlight_result(result_line)
                    self.step_status["step1_powerandlowlight_indicatorsactive"] = {
                        "status": "FAIL",
                    }
                    self.post_powerandlowlight_snapshot()
                    self.powerandlowlight_passed[0] = False
                    self.powerandlowlight_failed[0] = True
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_powerandlowlight_step == 1:
                msg1.setWindowTitle("Power Indicator Light Deactivated")
                msg1.setText("The Power Indicator Light has been deactivated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Power Indicator Light deactivates after being pressed: "
                    result_line += "\tPASS"
                    self.insert_powerandlowlight_result(result_line)
                    self.step_status["step2_powerandlowlight_indicatorsinactive"] = {
                        "status": "PASS",
                    }
                    self.post_powerandlowlight_snapshot()
                    self.powerandlowlight_passed[1] = True
                    self.powerandlowlight_failed[1] = False
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Power Indicator Light deactivates after being pressed: "
                    result_line += "\tFAIL"
                    self.insert_powerandlowlight_result(result_line)
                    self.step_status["step2_powerandlowlight_indicatorsinactive"] = {
                        "status": "FAIL",
                    }
                    self.post_powerandlowlight_snapshot()
                    self.powerandlowlight_passed[1] = False
                    self.powerandlowlight_failed[1] = True
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_powerandlowlight_step == 2:
                msg1.setWindowTitle("Power Indicator Light Activated")
                msg1.setText("No leaks found and the Power Indicator Light has been activated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"No tank leaks found and Power Indicator Light activated: "
                    result_line += "\tPASS"
                    self.insert_powerandlowlight_result(result_line)
                    self.step_status["step3_powerandlowlight_noleaks_indicatoractive"] = {
                        "status": "PASS",
                    }
                    self.post_powerandlowlight_snapshot()
                    self.powerandlowlight_passed[2] = True
                    self.powerandlowlight_failed[2] = False
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"No tank leaks found and Power Indicator Light activated: "
                    result_line += "\tFAIL"
                    self.insert_powerandlowlight_result(result_line)
                    self.step_status["step3_powerandlowlight_noleaks_indicatoractive"] = {
                        "status": "FAIL",
                    }
                    self.post_powerandlowlight_snapshot()
                    self.powerandlowlight_passed[2] = False
                    self.powerandlowlight_failed[2] = True
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_powerandlowlight_step == 3:
                    msg1.setWindowTitle("Power Indicator Light Deactivated")
                    msg1.setText("The Power Indicator Light has been deactivated.")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        result_line = f"Power Indicator Light deactivated: "
                        result_line += "\tPASS"
                        self.step_status["step4_powerandlowlight_indicator_inactive"] = {
                            "status": "PASS",
                        }
                        self.post_powerandlowlight_snapshot()
                        self.insert_powerandlowlight_result(result_line)
                        self.powerandlowlight_passed[3] = True
                        self.powerandlowlight_failed[3] = False
                        self.powerandlowlight_completed = True
                        self.updatePowerAndLowLightStep()
                        self.current_powerandlowlight_step += 1
                    elif msg1.clickedButton() == fail_button:
                        result_line = f"Power Indicator Light deactivated: "
                        result_line += "\tFAIL"
                        self.insert_powerandlowlight_result(result_line)
                        self.step_status["step4_powerandlowlight_indicator_inactive"] = {
                            "status": "FAIL",
                        }
                        self.post_powerandlowlight_snapshot()
                        self.powerandlowlight_passed[3] = False
                        self.powerandlowlight_failed[3] = True
                        self.powerandlowlight_completed = True
                        self.updatePowerAndLowLightStep()
                        self.current_powerandlowlight_step += 1


            # Completed
            elif self.powerandlowlight_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Power And Low Indicator Light test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updatePowerAndLowLightStep()

        except Exception as e:
            print(f"Error: {e}")

    def updatePowerAndLowLightStep(self):
        if self.powerandlowlight_passed[0] or self.powerandlowlight_failed[0]:
            self.powerandlowlightlabel.setText(
                "5. Press the POWER button.<br><br>"
                "<i>Power indicator should deactivate.</i><br><br>"
            )

            self.powerandlowlightbeginbutton.setText("Continue")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)

        if self.powerandlowlight_passed[1] or self.powerandlowlight_failed[1]:
            self.powerandlowlightlabel.setText(
                "6. Connect the water supply to the Beverage Maker by closing V11 and opening V10.<br><br>"
                "Once filled, ensure water pressure is set between 24 and 29 psig by assessing reading on PG2 (1.66 to 2.0 barg).<br><br>"
                "7. Make sure the Beverage Maker tank fills and no leaks are present. (A full tank is indicated by a reading of 0 on the flow meter (FM))<br><br>"
                "8. After the tank is filled, press the power button.<br><br>"
                "<i>The power indicator light should be activated.</i><br><br>"

            )

            self.powerandlowlightbeginbutton.setText("Continue")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)

        if self.powerandlowlight_passed[2] or self.powerandlowlight_failed[2]:
            self.powerandlowlightlabel.setText(
                "Make sure the LOW WATER indicator light is off and press the power button.<br><br>"
                "<i>The power light indicator should be deactivated.</i><br><br>"
            )
            self.powerandlowlightbeginbutton.setText("Continue")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)


        if self.powerandlowlight_passed[3] or self.powerandlowlight_failed[3]:
            self.powerandlowlightlabel.setText(
                "Test completed.<br><br>"
                "<i>The Power and Low Light indicator Test has been completed succssfully!</i><br><br>"
                )
            self.powerandlowlightbeginbutton.setText("Results")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLightResults)

            self.powerandlowlightrestart = QPushButton("Restart", self)
            self.powerandlowlightrestart.clicked.connect(self.PowerAndLowLightRestart)
            self.powerandlowlightrestart.setFixedWidth(200)
            self.powerandlowlighttestbuttonlayout.addWidget(self.powerandlowlightrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.powerandlowlightnext = QPushButton("Next", self)
            self.powerandlowlightnext.clicked.connect(self.PowerAndLowLightNext)
            self.powerandlowlightnext.setFixedWidth(200)
            self.powerandlowlighttestbuttonlayout.addWidget(self.powerandlowlightnext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def PowerAndLowLightNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetPowerAndLowLightResults(self):
        return self.powerandlowlight_results

    def PowerAndLowLightTestPath(self, path):
        self.test_path = path

    def insert_powerandlowlight_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Power and Low Indicator Light Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Power and Low Light Indicator section not found.")
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

    def PowerAndLowLightRestart(self):
        print("Restarting PowerAndLowLight Test")

    def PowerAndLowLightResults(self):
        print("Printing PowerAndLowLight Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[PowerAndLowLight] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostPowerAndLowLightResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Power and Low Light: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/powerandlowlight"
            r = requests.post(url, json=payload, timeout=5)
            print("Power and Low Light POST status:", r.status_code)
            print("Power and Low Light POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Power and Low Light result: {e}")

    def post_powerandlowlight_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.powerandlowlight_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.powerandlowlight_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.powerandlowlight_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostPowerAndLowLightResults(status=overall_status, data=data, notes=notes)