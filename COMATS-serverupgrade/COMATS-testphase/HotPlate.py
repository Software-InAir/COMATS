from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog, QComboBox
)

from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal, QUrl

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



#------------------------------------------------------- HotPlate Check

class HotPlateTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.hotplate_results = ""
        self.hotplate_passed = [False, False, False, False]
        self.hotplate_failed = [False, False, False, False]
        self.hotplate_completed = False
        self.current_hotplate_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.hotplatelabellayout = QHBoxLayout()
        self.hotplatetestbuttonlayout = QHBoxLayout()

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

        self.hotplatelabel = QLabel(
            "<b>Press the HOT PLATE button and verify that the HOT PLATE indicator turns on.</b><br><br>"
        )

        self.hotplatelabel.setTextFormat(Qt.TextFormat.RichText)
        self.hotplatelabel.setWordWrap(True)
        self.hotplatelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.hotplatelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.hotplatelabel)


        self.hotplatelabellayout.addWidget(scroll)
        layout.addLayout(self.hotplatelabellayout)
        layout.addLayout(self.hotplatetestbuttonlayout)
        try:
            self.hotplatebeginbutton = QPushButton("Begin")
            self.hotplatebeginbutton.setFixedWidth(200)
            self.hotplatebeginbutton.clicked.connect(self.HotPlate)
            self.hotplatetestbuttonlayout.addWidget(self.hotplatebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def HotPlate(self):
        try:

                msg1 = QMessageBox()
                # msg1.setIcon(QMessageBox.Icon.Information)

                if self.current_hotplate_step == 1:
                    msg1.setWindowTitle("Hot Plate Temperature")
                    msg1.setText("Hot Plate Temperature reaches and/or exceeds 130 degrees.")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        result_line = f"Hot Plate Temperature: "
                        result_line += "\tPASS"
                        self.insert_hotplate_result(result_line)
                        self.step_status["step2_hotplate_temp"] = {
                            "status": "PASS",
                        }
                        self.post_hotplate_snapshot()
                        self.hotplate_passed[1] = True
                        self.hotplate_failed[1] = False
                        self.hotplate_completed = True
                        self.updateHotPlateStep()
                        self.current_hotplate_step += 1
                        self.hotplate_completed = True
                    elif msg1.clickedButton() == fail_button:
                        result_line = f"Hot Plate Temperature: "
                        result_line += "\tFAIL"
                        self.insert_hotplate_result(result_line)
                        self.step_status["step1_hotplate_temp"] = {
                            "status": "FAIL",
                        }
                        self.post_hotplate_snapshot()
                        self.hotplate_passed[1] = False
                        self.hotplate_failed[1] = True
                        self.updateHotPlateStep()
                        self.current_hotplate_step += 1
                        self.hotplate_completed = True


                elif self.current_hotplate_step == 0:
                    msg1.setWindowTitle("Hot Plate Indicator Light")
                    msg1.setText("Hot Plate Indicator Light illuminated.")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        result_line = f"Hot Plate Indicator Light: "
                        result_line += "\tPASS"
                        self.insert_hotplate_result(result_line)
                        self.step_status["step2_hotplate_indicator"] = {
                            "status": "PASS",
                        }
                        self.post_hotplate_snapshot()
                        self.hotplate_passed[0] = True
                        self.hotplate_failed[0] = False
                        self.updateHotPlateStep()
                        self.current_hotplate_step += 1

                    elif msg1.clickedButton() == fail_button:
                        result_line = f"Hot Plate Indicator Light: "
                        result_line += "\tFAIL"
                        self.insert_hotplate_result(result_line)
                        self.step_status["step1_hotplate_indicator"] = {
                            "status": "PASS",
                        }
                        self.post_hotplate_snapshot()
                        self.hotplate_passed[0] = False
                        self.hotplate_failed[0] = True
                        self.updateHotPlateStep()
                        self.current_hotplate_step += 1




                # Completed
                elif self.hotplate_completed:
                    msg1.setWindowTitle("Test Completed!")
                    msg1.setText("The HotPlate test has been completed successfully.")
                    msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                    msg1.exec()

                    self.updateHotPlateStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHotPlateStep(self):

        if self.hotplate_passed[0] or self.hotplate_failed[0]:
            print("Update Hot Plate Step")
            self.hotplatelabel.setText(
                "<b>Verify that the hot plate gets hot by touching temperature probe to hot plate. </b><br><br>"
                "<i> The temperature should reach 130°F at minimum. </i><br><br>"
            )
            self.hotplatebeginbutton.setText("Continue")
            self.hotplatebeginbutton.clicked.disconnect()
            self.hotplatebeginbutton.clicked.connect(self.HotPlate)


        if self.hotplate_completed == True:
            self.hotplatelabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Hot Plate test has been completed successfully!</b><br><br>"
            )
            self.hotplatebeginbutton.setText("Results")
            self.hotplatebeginbutton.clicked.disconnect()
            self.hotplatebeginbutton.clicked.connect(self.HotPlateResults)

            self.hotplaterestart = QPushButton("Restart", self)
            self.hotplaterestart.clicked.connect(self.HotPlateRestart)
            self.hotplaterestart.setFixedWidth(200)
            self.hotplatetestbuttonlayout.addWidget(self.hotplaterestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.hotplatenext = QPushButton("Next", self)
            self.hotplatenext.clicked.connect(self.HotPlateNext)
            self.hotplatenext.setFixedWidth(200)
            self.hotplatetestbuttonlayout.addWidget(self.hotplatenext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def HotPlateNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetHotPlateResults(self):
        return self.hotplate_results

    def HotPlateTestPath(self, path):
        self.test_path = path

    def insert_hotplate_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Hot Plate Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Hot Plate section not found.")
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

    def HotPlateRestart(self):
        print("Restarting Hot Plate Test")

    def HotPlateResults(self):
        print("Printing Hot Plate Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[HotPlate] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostHotPlateResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Hot Platet: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/hotplate"
            r = requests.post(url, json=payload, timeout=5)
            print("Hot Plat POST status:", r.status_code)
            print("Hot Plate Current POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Heater Current result: {e}")

    def post_hotplate_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.hotplate_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.hotplate_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.hotplate_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostHotPlateResults(status=overall_status, data=data, notes=notes)


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
            CMMLoader.addItems(["25-33-20"])
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