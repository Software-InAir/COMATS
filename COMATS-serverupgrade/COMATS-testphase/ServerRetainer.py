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



#------------------------------------------------------- ServerRetainer Check

class ServerRetainerTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None

        self.serverretainer_results = ""
        self.serverretainer_passed = [False, False, False]
        self.serverretainer_failed = [False, False, False]
        self.serverretainer_completed = False
        self.current_serverretainer_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.serverretainerlabellayout = QHBoxLayout()
        self.serverretainertestbuttonlayout = QHBoxLayout()

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

        self.serverretainerlabel = QLabel(
            "<b>With a server and the brew cup installed, lower the brew handle.<br><br>"
            "Pull on the server to make sure the server retainer is working correctly.</b><br><br>"
            "<i>Server should remain firmly in place</i><br><br>"


        )

        self.serverretainerlabel.setTextFormat(Qt.TextFormat.RichText)
        self.serverretainerlabel.setWordWrap(True)
        self.serverretainerlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.serverretainerlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.serverretainerlabel)


        self.serverretainerlabellayout.addWidget(scroll)
        layout.addLayout(self.serverretainerlabellayout)
        layout.addLayout(self.serverretainertestbuttonlayout)
        try:
            self.serverretainerbeginbutton = QPushButton("Begin")
            self.serverretainerbeginbutton.setFixedWidth(200)
            self.serverretainerbeginbutton.clicked.connect(self.ServerRetainer)
            self.serverretainertestbuttonlayout.addWidget(self.serverretainerbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def ServerRetainer(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_serverretainer_step == 0:
                msg1.setWindowTitle("Check Server Retainer")
                msg1.setText("Server remains in place.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Server Retainer Test: "
                    result_line += "\tPASS"
                    self.insert_serverretainer_result(result_line)
                    self.step_status["step1_serverretainer_immobile"] = {
                        "status": "PASS",
                    }
                    self.post_serverretainer_snapshot()
                    self.serverretainer_passed[0] = True
                    self.serverretainer_failed[0] = False
                    self.serverretainer_completed = True
                    self.updateServerRetainerStep()
                    self.current_serverretainer_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Server Retainer Test: "
                    result_line += "\tFAIL"
                    self.insert_serverretainer_result(result_line)
                    self.step_status["step1_serverretainer_immobile"] = {
                        "status": "FAIL",
                    }
                    self.post_serverretainer_snapshot()
                    self.serverretainer_passed[0] = False
                    self.serverretainer_failed[0] = True
                    self.updateServerRetainerStep()
                    self.current_serverretainer_step += 1


            # Completed
            elif self.serverretainer_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The ServerRetainer test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateServerRetainerStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateServerRetainerStep(self):

        if self.serverretainer_passed[0] or self.serverretainer_failed[0]:
            self.serverretainerlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Server Retainer test has been completed successfully!</b><br><br>"
            )
            self.serverretainerbeginbutton.setText("Results")
            self.serverretainerbeginbutton.clicked.disconnect()
            self.serverretainerbeginbutton.clicked.connect(self.ServerRetainerResults)

            self.serverretainerrestart = QPushButton("Restart", self)
            self.serverretainerrestart.clicked.connect(self.ServerRetainerRestart)
            self.serverretainerrestart.setFixedWidth(200)
            self.serverretainertestbuttonlayout.addWidget(self.serverretainerrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.severretainernext = QPushButton("Next", self)
            self.severretainernext.clicked.connect(self.ServerRetainerNext)
            self.severretainernext.setFixedWidth(200)
            self.severretainertestbuttonlayout.addWidget(self.severretainernext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def ServerRetainerNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetServerRetainerResults(self):
        return self.serverretainer_results

    def ServerRetainerTestPath(self, path):
        self.test_path = path

    def insert_serverretainer_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Server Retainer Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Server Retainer section not found.")
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

    def ServerRetainerRestart(self):
        print("Restarting ServerRetainer Test")

    def ServerRetainerResults(self):
        print("Printing ServerRetainer Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[ServerRetainer] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostServerRetainerResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("ServerRetainer: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/serverretainer"
            r = requests.post(url, json=payload, timeout=5)
            print("ServerRetainer POST status:", r.status_code)
            print("ServerRetainer POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting ServerRetainer result: {e}")

    def post_serverretainer_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.serverretainer_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.serverretainer_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.serverretainer_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostServerRetainerResults(status=overall_status, data=data, notes=notes)