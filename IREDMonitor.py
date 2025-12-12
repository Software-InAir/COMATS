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



#------------------------------------------------------- IREDMonitor Check

class IREDMonitorTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.iredmonitor_results = ""
        self.iredmonitor_passed = [False, False, False, False]
        self.iredmonitor_failed = [False, False, False, False]
        self.iredmonitor_completed = False
        self.current_iredmonitor_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.iredmonitorlabellayout = QHBoxLayout()
        self.iredmonitortestbuttonlayout = QHBoxLayout()

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

        self.iredmonitorlabel = QLabel(
            "<b>With the brew handle raised, insert a piece of 0.125 inch black heat shrink tubing into the left optical sensor cavity to block the infra-red beam.</b> <br><br>"
            "<i>The circuit breaker should open as indicated by hearing an audible clicking noise as the circuit breaker is pushed out on the back of unit. This will reveal a white inner core.</i> <br><br>"



        )

        self.iredmonitorlabel.setTextFormat(Qt.TextFormat.RichText)
        self.iredmonitorlabel.setWordWrap(True)
        self.iredmonitorlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.iredmonitorlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.iredmonitorlabel)


        self.iredmonitorlabellayout.addWidget(scroll)
        layout.addLayout(self.iredmonitorlabellayout)
        layout.addLayout(self.iredmonitortestbuttonlayout)
        try:
            self.iredmonitorbeginbutton = QPushButton("Begin")
            self.iredmonitorbeginbutton.setFixedWidth(200)
            self.iredmonitorbeginbutton.clicked.connect(self.IREDMonitor)
            self.iredmonitortestbuttonlayout.addWidget(self.iredmonitorbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def IREDMonitor(self):
        try:
            msg1 = QMessageBox()

            if self.current_iredmonitor_step == 0:
                msg1.setWindowTitle("Circuit Breaker")
                msg1.setText("Circuit breaker activated on back of current UUT after audible click.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"IRED Monitor Test: "
                    result_line += "\tPASS"
                    self.insert_iredmonitor_result(result_line)
                    self.step_status["step1_iredmonitor_circuitbreaker"] = {
                        "status": "PASS",
                    }
                    self.post_iredmonitor_snapshot()
                    self.iredmonitor_passed[0] = True
                    self.iredmonitor_failed[0] = False
                    self.current_iredmonitor_step += 1
                    self.iredmonitor_completed = True
                    self.updateIREDMonitorStep()


                elif msg1.clickedButton() == fail_button:
                    result_line = f"IRED Monitor Test: "
                    result_line += "\tFAIL"
                    self.insert_iredmonitor_result(result_line)
                    self.step_status["step1_iredmonitor_circuitbreaker"] = {
                        "status": "FAIL",
                    }
                    self.post_iredmonitor_snapshot()
                    self.iredmonitor_passed[0] = False
                    self.iredmonitor_failed[0] = True
                    self.iredmonitor_completed = True
                    self.updateIREDMonitorStep()



            elif self.current_iredmonitor_step == 1:
                value1, ok = NumericKeypadDialog.getValue(
                    self,
                    "Brew Flow",
                    "Please enter the flow rate indicated on FM",
                    decimals=2,
                    min_value=0.0,
                    max_value=200.0,
                )
                self.iredmonitor_results += f""
                if ok:
                    result_line = f"Brew Flow: {value1}GPM \n"
                    if value1 == 0:
                        result_line += "\tPASS"
                        self.step_status["step2_iredmonitor_flow"] = {
                            "status": "PASS",
                            "value": value1,
                        }
                        self.post_iredmonitor_snapshot()
                        self.iredmonitor_passed[1] = True
                        self.iredmonitor_failed[1] = False
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step2_iredmonitor_flow"] = {
                            "status": "FAIL",
                            "value": value1,
                        }
                        self.post_iredmonitor_snapshot()
                        self.iredmonitor_passed[1] = False
                        self.iredmonitor_failed[1] = True

                    self.insert_iredmonitor_result(result_line)
                    self.current_iredmonitor_step += 1
                    self.iredmonitor_completed = True
                    self.updateIREDMonitorStep()




            # Completed
            elif self.iredmonitor_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The IRED Monitor test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateIREDMonitorStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateIREDMonitorStep(self):

        if self.iredmonitor_passed[0] or self.iredmonitor_failed[0]:
            print("Update IRED Monitor Step")
            self.iredmonitorlabel.setText(
                 "<i>The brew flow should cease as indicated by a value of zero indicated on FM.</i> <br><br>"
                 "<b> Brew flow will not resume.</b><br><br>"

            )
            self.iredmonitorbeginbutton.setText("Continue")
            self.iredmonitorbeginbutton.clicked.disconnect()
            self.iredmonitorbeginbutton.clicked.connect(self.IREDMonitor)


        if self.iredmonitor_completed == True:
            self.iredmonitorlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The IRED Monitor test has been completed successfully!</b><br><br>"
                "<b>Please reset circuit breaker by depressing core into unit.</b> <br><br>"
            )
            self.iredmonitorbeginbutton.setText("Results")
            self.iredmonitorbeginbutton.clicked.disconnect()
            self.iredmonitorbeginbutton.clicked.connect(self.IREDMonitorResults)

            self.iredmonitorrestart = QPushButton("Restart", self)
            self.iredmonitorrestart.clicked.connect(self.IREDMonitorRestart)
            self.iredmonitorrestart.setFixedWidth(200)
            self.iredmonitortestbuttonlayout.addWidget(self.iredmonitorrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.iredmonitornext = QPushButton("Next", self)
            self.iredmonitornext.clicked.connect(self.IREDMonitorNext)
            self.iredmonitornext.setFixedWidth(200)
            self.iredmonitortestbuttonlayout.addWidget(self.iredmonitornext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def IREDMonitorNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetIREDMonitorResults(self):
        return self.iredmonitor_results

    def IREDMonitorTestPath(self, path):
        self.test_path = path

    def insert_iredmonitor_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>IRED Monitor Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("IRED Monitor section not found.")
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

    def IREDMonitorRestart(self):
        print("Restarting IRED Monitor Test")

    def IREDMonitorResults(self):
        print("Printing IRED Monitor Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[IREDMonitor] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostIREDMonitorResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Heater Current: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/iredmonitor"
            r = requests.post(url, json=payload, timeout=5)
            print("Heater Current POST status:", r.status_code)
            print("Heater Current POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Heater Current result: {e}")

    def post_iredmonitor_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.iredmonitor_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.iredmonitor_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.iredmonitor_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostIREDMonitorResults(status=overall_status, data=data, notes=notes)

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

    def _base_dir(self):
        return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(
            __file__).resolve().parent

    def start_webgl(self):
        self.locator_window = QMainWindow()
        self.locator_window.setWindowTitle("Parts Locator")
        self.locator_window.resize(1200, 800)

        self.appcontainer = QWidget()
        self.locatorlayout = QVBoxLayout(self.appcontainer)
        html = self._base_dir() / "Unity" / "WebGL" / "index.html"

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