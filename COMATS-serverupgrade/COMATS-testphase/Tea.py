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



#------------------------------------------------------- Tea Check

class TeaTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()
        self.setMinimumSize(1200, 600)

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.tea_results = ""
        self.tea_passed = [False, False, False]
        self.tea_failed = [False, False, False]
        self.tea_completed = False
        self.current_tea_step = 0
        
        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.ambientlabellayout = QHBoxLayout()

        teatestbuttonlayout = QHBoxLayout()

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

        self.tealabel = QLabel(
            "<b>Is the tea option installed on current unit?</b><br><br>"

        )

        self.tealabel.setTextFormat(Qt.TextFormat.RichText)
        self.tealabel.setWordWrap(True)
        self.tealabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.tealabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.tealabel)

        self.ambientlabellayout.addWidget(scroll)
        layout.addLayout(self.ambientlabellayout)
        layout.addLayout(teatestbuttonlayout)
        try:
            self.teabeginbutton = QPushButton("Begin")
            self.teabeginbutton.setFixedWidth(200)
            self.teabeginbutton.clicked.connect(self.Tea)
            teatestbuttonlayout.addWidget(self.teabeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def Tea(self):
        try:
            msg1 = QMessageBox()
            # msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_tea_step == 0:
                msg1.setWindowTitle("Option Check")
                msg1.setText("Tea option installed on current unit.")
                pass_button = msg1.addButton("Yes", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("No", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Tea Option: "
                    result_line += "\tINSTALLED"
                    self.insert_tea_result(result_line)
                    self.step_status["step1_tea_installed"] = {
                        "status": "PASS",
                    }
                    self.post_tea_snapshot()
                    self.tea_passed[0] = True
                    self.tea_failed[0] = False
                    self.updateTeaStep()
                    self.current_tea_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Tea Option: "
                    result_line += "\tNOT INSTALLED"
                    self.insert_tea_result(result_line)
                    self.step_status["step1_tea_installed"] = {
                        "status": "FAIL",
                    }
                    self.post_tea_snapshot()
                    self.tea_passed[0] = False
                    self.tea_failed[0] = True
                    self.updateTeaStep()
                    self.current_tea_step += 1


            elif self.current_tea_step == 1:
                print(f"You are at step {self.current_tea_step}")
                value, ok = QInputDialog.getText(
                self,
                "Time Elapsed",
                "Please enter the time elapsed during tea brew cycle:")

                if ok:
                    time_str = value
                    print(time_str)

                    self.total_time = int(time_str[0])*60 + int(time_str[2])*10 + int(time_str[3])
                    result_line = f"Tea Cycle Time Elapsed Test: {value} "
                    if self.total_time <= 200 and self.total_time >= 150:

                        result_line += "\tPASS"
                        self.step_status["step2_tea_time"] = {
                            "status": "PASS",
                            "value": self.total_time,
                        }
                        self.post_tea_snapshot()
                        self.tea_passed[1] = True
                        self.tea_failed[1] = False
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step2_tea_time"] = {
                            "status": "FAIL",
                            "value": self.total_time,
                        }
                        self.post_tea_snapshot()
                        self.tea_passed[1] = False
                        self.tea_failed[1] = True

                    self.insert_tea_result(result_line)
                    print(f"User entered: {value}")
                    self.tea_results += f"Time elapsed Result: {self.total_time}\n"
                    self.updateTeaStep()
                    self.current_tea_step += 1


            elif self.current_tea_step == 2:
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
                    if value < 150:
                        tempsystem = "°C"
                    else:
                        tempsystem = "°F"
                    result_line = f"Tea Temperature Test: {value}{tempsystem} "
                    if tempsystem == "°F":
                        if value >= 175 and value <= 195:
                            result_line += "\tPASS"
                            self.step_status["step3_tea_temp"] = {
                                "status": "PASS",
                                "value": value,
                            }
                            self.post_tea_snapshot()
                            self.tea_passed[2] = True
                            self.tea_failed[2] = False
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step3_tea_temp"] = {
                                "status": "FAIL",
                                "value": value,
                            }
                            self.post_tea_snapshot()
                            self.tea_passed[2] = False
                            self.tea_failed[2] = True
                    elif tempsystem == "°C":
                        if value >= 79 and value <= 91:
                            result_line += "\tPASS"
                            self.step_status["step3_tea_temp"] = {
                                "status": "PASS",
                                "value": value,
                            }
                            self.post_tea_snapshot()
                            self.tea_passed[2] = True
                            self.tea_failed[2] = False
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step3_tea_temp"] = {
                                "status": "FAIL",
                                "value": value,
                            }
                            self.post_tea_snapshot()
                            self.tea_passed[2] = False
                            self.tea_failed[2] = True
                    self.insert_tea_result(result_line)
                    print(f"User entered: {value}{tempsystem}")
                    self.tea_results += f"Tea Temperature Result: {value}{tempsystem}\n"
                    self.updateTeaStep()
                    self.current_tea_step += 1

            else:
                print("Tea option not installed.")

        except Exception as e:
            print(f"Error: {e}")

    def updateTeaStep(self):

        if self.tea_passed[0] or self.tea_failed[0]:
            self.tealabel.setText(
                "<b>Verify that V8 is horizontal<br><br>"
                "a. <i>The warmer (where option is installed) must be on before starting this test.</i><br><br>"
                "Put an empty server in the Beverage Maker and lower the brew handle.<br><br>"
                "The water supply pressure should be set to 24 to 29 psig (1.66 to 2.0 barg).<br><br>"
                "Ensure this by checking the reading on PG2. <br><br>"
                "b. Press the TEA button and observe the flow meter (FM).<br>"
                "When flow starts, simultaneously begin the stopwatch. <br><br>"
                "NOTE: Tea brew does not start until the water in the tank is heated.<br><br>"
                "c. Stop the stopwatch when the flow meter (FM) goes to zero flow.</b><br><br>"
                "<i>Elapsed time between when flow starts and stops should be 2 min. 30 sec. to 3 min. 20 sec.</i><br><br>"

            )

            self.teabeginbutton.setText("Continue")
            self.teabeginbutton.clicked.disconnect()
            self.teabeginbutton.clicked.connect(self.Tea)

        if self.tea_passed[1] or self.tea_failed[1]:
            self.tealabel.setText(
                "<b>d. Lift the brew handle and measure the temperature of liquid in the server using the digital thermometer.<br><br>"
                "<i>The temperature should be between 175° F (79° C) and 195° F 91° C)and the server should be full. .</i><br><br> "
                "e.Empty the server and install back into the Beverage Maker.<br><br>"
                "Lower the brew handle.<br><br></b>"
            )
            self.teabeginbutton.setText("Continue")
            self.teabeginbutton.clicked.disconnect()
            self.teabeginbutton.clicked.connect(self.Tea)


        if self.tea_passed[2] or self.tea_failed[2]:
            self.tealabel.setText(
                "<b>Test Complete.</b><br><br>"
                "<b>The Tea Test has been completed successfully!<br><br>"
            )
            self.teabeginbutton.setText("Results")
            self.teabeginbutton.clicked.disconnect()
            self.teabeginbutton.clicked.connect(self.TeaResults)

            self.tearestart = QPushButton("Restart", self)
            self.tearestart.clicked.connect(self.TeaRestart)
            self.tearestart.setFixedWidth(200)
            self.teatestbuttonlayout.addWidget(self.tearestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.teanext = QPushButton("Next", self)
            self.teanext.clicked.connect(self.TeaNext)
            self.teanext.setFixedWidth(200)
            self.teatestbuttonlayout.addWidget(self.teanext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def TeaNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetTeaResults(self):
        return self.tea_results

    def TeaTestPath(self, path):
        self.test_path = path

    def insert_tea_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Tea Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Tea section not found.")
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

    def TeaRestart(self):
        print("Restarting Tea Test")

    def TeaResults(self):
        print("Printing Tea Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[Tea] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostTeaResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Tea: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/tea"
            r = requests.post(url, json=payload, timeout=5)
            print("Tea POST status:", r.status_code)
            print("Tea POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Tea result: {e}")

    def post_tea_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.tea_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.tea_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.tea_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostTeaResults(status=overall_status, data=data, notes=notes)


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