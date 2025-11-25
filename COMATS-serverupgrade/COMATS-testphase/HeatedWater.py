from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal

from InstrumentWorker import InstrumentWorker

from NumPad import NumericKeypadDialog


import requests

class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- HeatedWater Check

class HeatedWaterTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None,  parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None

        self.heatedwater_results = ""
        self.heatedwater_passed = [False, False, False, False]
        self.heatedwater_failed = [False, False, False, False]
        self.heatedwater_completed = False
        self.current_heatedwater_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.heatedwaterlabellayout = QHBoxLayout()
        self.heatedwatertestbuttonlayout = QHBoxLayout()

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

        self.heatedwaterlabel = QLabel(
            "<b> Place server under faucet. <br><br>"
            "   Push the HOT WATER button and verify that heated water comes out of the faucet. </b> <br><br>"
            "<i> Verify flow rate is greater than 0.23 gallons per minute as indicated by FM. </i>"

        )

        self.heatedwaterlabel.setTextFormat(Qt.TextFormat.RichText)
        self.heatedwaterlabel.setWordWrap(True)
        self.heatedwaterlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.heatedwaterlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.heatedwaterlabel)


        self.heatedwaterlabellayout.addWidget(scroll)
        layout.addLayout(self.heatedwaterlabellayout)
        layout.addLayout(self.heatedwatertestbuttonlayout)
        try:
            self.heatedwaterbeginbutton = QPushButton("Begin")
            self.heatedwaterbeginbutton.setFixedWidth(200)
            self.heatedwaterbeginbutton.clicked.connect(self.HeatedWater)
            self.heatedwatertestbuttonlayout.addWidget(self.heatedwaterbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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



    def HeatedWater(self):
        try:

                msg1 = QMessageBox()
                # msg1.setIcon(QMessageBox.Icon.Information)

                if self.current_heatedwater_step == 0:
                    value1, ok = NumericKeypadDialog.getValue(
                        parent=self,
                        title="Flow Rate Measurement",
                        label="Please enter the flow rate as indicated by FM ",
                        initial=0,
                        decimals=2,
                        min_value=0.0,
                        max_value=200.0,
                    )
                    self.heatedwater_results += f""
                    if ok:
                        result_line = f"Heated Water Flow Rate: {value1}GPM \n"
                        if value1 >= 0.23:
                            result_line += "\tPASS"
                            self.step_status["step1_heatedwater_flowrate"] = {
                                "status": "PASS",
                                "value": value1
                            }
                            self.post_heatedwater_snapshot()
                            self.heatedwater_passed[0] = True
                            self.heatedwater_failed[0] = False
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step1_heatedwater_flowrate"] = {
                                "status": "FAIL",
                                "value": value1
                            }
                            self.post_heatedwater_snapshot()
                            self.heatedwater_passed[0] = False
                            self.heatedwater_failed[0] = True
                        self.insert_heatedwater_result(result_line)
                        self.current_heatedwater_step += 1
                        self.heatedwater_completed = True
                        self.updateHeatedWaterStep()



                # Completed
                elif self.heatedwater_completed:
                    msg1.setWindowTitle("Test Completed!")
                    msg1.setText("The HeatedWater test has been completed successfully.")
                    msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                    msg1.exec()

                    self.updateHeatedWaterStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHeatedWaterStep(self):


        if self.heatedwater_completed == True:
            self.heatedwaterlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Heated Water test has been completed successfully!</b><br><br>"
            )
            self.heatedwaterbeginbutton.setText("Results")
            self.heatedwaterbeginbutton.clicked.disconnect()
            self.heatedwaterbeginbutton.clicked.connect(self.HeatedWaterResults)

            self.heatedwaterrestart = QPushButton("Restart", self)
            self.heatedwaterrestart.clicked.connect(self.HeatedWaterRestart)
            self.heatedwaterrestart.setFixedWidth(200)
            self.heatedwatertestbuttonlayout.addWidget(self.heatedwaterrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.heatedwaternext = QPushButton("Next", self)
            self.heatedwaternext.clicked.connect(self.HeatedWaterNext)
            self.heatedwaternext.setFixedWidth(200)
            self.heatedwatertestbuttonlayout.addWidget(self.heatedwaternext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def HeatedWaterNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetHeatedWaterResults(self):
        return self.heatedwater_results

    def HeatedWaterTestPath(self, path):
        self.test_path = path

    def insert_heatedwater_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Heated Water Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Heated Water section not found.")
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

    def HeatedWaterRestart(self):
        print("Restarting HeatedWater Test")

    def HeatedWaterResults(self):
        print("Printing HeatedWater Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[HeatedWater] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostHeatedWaterResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Heated Water: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/heatedwater"
            r = requests.post(url, json=payload, timeout=5)
            print("Heated Water POST status:", r.status_code)
            print("Heated Water POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Heated Water result: {e}")

    def post_heatedwater_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.heatedwater_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.heatedwater_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.heatedwater_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostHeatedWaterResults(status=overall_status, data=data, notes=notes)