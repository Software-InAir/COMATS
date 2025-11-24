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



#------------------------------------------------------- BrewBE Check

class BrewBETest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker

        self.test_id: int | None = None
        self.api_base_url: str | None = None

        self.brewbe_results = ""
        self.brewbe_passed = [False, False, False, False]
        self.brewbe_failed = [False, False, False, False]
        self.brewbe_completed = False
        self.current_brewbe_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.brewbelabellayout = QHBoxLayout()
        self.brewbetestbuttonlayout = QHBoxLayout()

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

        self.brewbelabel = QLabel(
            "<b>    Starting with a hot tank as indicated by HOT WATER light being illuminated, use a stopwatch to time "
            "       a brew cycle from when the BREW button is pushed until the BREW button light goes out. </b><br><br>"
            "  <i> The brew cycle time for Coffee Maker PN 11225-31 should be 2 minutes 30 seconds ±40 seconds. </i><br><br>"
            "<b> All other Coffee Makers should have a brew cycle time of 3 minutes 15 seconds ±40 seconds. <br><br>"
            "<i>NOTE: Brews started in mid cycle can be extended by a recovery time of up to 90 seconds.</i></b><br><br>"

        )

        self.brewbelabel.setTextFormat(Qt.TextFormat.RichText)
        self.brewbelabel.setWordWrap(True)
        self.brewbelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.brewbelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.brewbelabel)


        self.brewbelabellayout.addWidget(scroll)
        layout.addLayout(self.brewbelabellayout)
        layout.addLayout(self.brewbetestbuttonlayout)
        try:
            self.brewbebeginbutton = QPushButton("Begin")
            self.brewbebeginbutton.setFixedWidth(200)
            self.brewbebeginbutton.clicked.connect(self.BrewBE)
            self.brewbetestbuttonlayout.addWidget(self.brewbebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(brewbe, f"BrewBE")

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

    def BrewBE(self):
        try:

                msg1 = QMessageBox()
                # msg1.setIcon(QMessageBox.Icon.Information)

                if self.current_brewbe_step == 0:
                    value1, ok = QInputDialog.getDouble(
                        self,
                        "Phase A",
                        "Please enter the time elapsed during brew cycle in seconds.",
                        decimals=0,
                        min=0.0,
                        max=500.0,
                        step=.01
                    )
                    self.brewbe_results += f""
                    if ok:
                        result_line = f"Brew Cycle Duration: {value1} seconds\n"
                        if value1 >= 110 and value1 <= 190:
                            result_line += "\tPASS"
                            self.step_status["step1_brew_time"] = {
                                "status": "PASS",
                                "value": value1
                            }
                            self.post_brewbe_snapshot()
                            self.brewbe_passed[0] = True
                            self.brewbe_failed[0] = False
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step1_brew_time"] = {
                                "status": "FAIL",
                                "value": value1
                            }
                            self.post_brewbe_snapshot()
                            self.brewbe_passed[0] = False
                            self.brewbe_failed[0] = True
                        self.insert_brewbe_result(result_line)
                        self.current_brewbe_step += 1
                        self.updateBrewBEStep()


                elif self.current_brewbe_step == 1:
                    value1, ok = QInputDialog.getDouble(
                        self,
                        "Water Level",
                        "Please enter the water level as measured in inches.",
                        value=0.00,
                        decimals=2,
                        min=0.00,
                        max=100.00,
                        step=.01
                    )
                    self.brewbe_results += f""
                    if ok:
                        result_line = f"Water Level: {value1} inches\n"
                        if value1 >= 110 and value1 <= 190:
                            result_line += "\tPASS"
                            self.step_status["step2_brew_level"] = {
                                "status": "PASS",
                                "value": value1
                            }
                            self.post_brewbe_snapshot()
                            self.brewbe_passed[1] = True
                            self.brewbe_failed[1] = False
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step2_brew_level"] = {
                                "status": "PASS",
                                "value": value1
                            }
                            self.post_brewbe_snapshot()
                            self.brewbe_passed[1] = False
                            self.brewbe_failed[1] = True
                        self.insert_brewbe_result(result_line)
                        self.current_brewbe_step += 1
                        self.brewbe_completed = True
                        self.updateBrewBEStep()


                # Completed
                elif self.brewbe_completed:
                    msg1.setWindowTitle("Test Completed!")
                    msg1.setText("The Brew test has been completed successfully.")
                    msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                    msg1.exec()

                    self.updateBrewBEStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateBrewBEStep(self):

        if self.brewbe_passed[0] or self.brewbe_failed[0]:
            print("Update Brew Step")
            self.brewbelabel.setText(
                "<i>The server level measured in a 64-ounce server should be 4.1±0.3 inches measured with level measuring tool.</i><br><br>"

            )
            self.brewbebeginbutton.setText("Continue")
            self.brewbebeginbutton.clicked.disconnect()
            self.brewbebeginbutton.clicked.connect(self.BrewBE)

        if self.brewbe_passed[1] or self.brewbe_failed[1]:
            print("Update Brew Step")
            self.brewbelabel.setText(
                " <b>  Each heater should draw approximately 8±1 amps</b> <br><br>"
                " <i>  Please enter the amperage of Phase A as displayed by the self.phase readings window </i><br><br>"
            )
            self.brewbebeginbutton.setText("Continue")
            self.brewbebeginbutton.clicked.disconnect()
            self.brewbebeginbutton.clicked.connect(self.BrewBE)


        if self.brewbe_completed == True:
            self.brewbelabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Brew test has been completed successfully!</b><br><br>"
                "<b> Please empty server and replace.</b>"
            )
            self.brewbebeginbutton.setText("Results")
            self.brewbebeginbutton.clicked.disconnect()
            self.brewbebeginbutton.clicked.connect(self.BrewBEResults)

            self.brewberestart = QPushButton("Restart", self)
            self.brewberestart.clicked.connect(self.BrewBERestart)
            self.brewberestart.setFixedWidth(200)
            self.brewbetestbuttonlayout.addWidget(self.brewberestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetBrewBEResults(self):
        return self.brewbe_results

    def BrewBETestPath(self, path):
        self.test_path = path

    def insert_brewbe_result(self, result_line: str):
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

    def BrewBERestart(self):
        print("Restarting BrewBE Test")

    def BrewBEResults(self):
        print("Printing BrewBE Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[BrewBE] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostBrewBEResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Brew BE: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/brewbe"
            r = requests.post(url, json=payload, timeout=5)
            print("Brew BE POST status:", r.status_code)
            print("Brew BE POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Brew BE result: {e}")

    def post_brewbe_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.brewbe_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.brewbe_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.brewbe_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostBrewBEResults(status=overall_status, data=data, notes=notes)