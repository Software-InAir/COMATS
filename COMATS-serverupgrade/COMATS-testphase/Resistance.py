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



#------------------------------------------------------- Resistance Check

class ResistanceTest(QWidget):
    resistance_results = ""


    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.resistance_results = f""

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.resistance_passed = [False, False, False]
        self.resistance_failed = [False, False, False]
        self.resistance_completed = False
        self.current_resistance_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.resistancelabellayout = QHBoxLayout()
        resistancetestbuttonlayout = QHBoxLayout()

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

        self.resistancelabel = QLabel(
            "<b>Turn QuadTech Milliohm Meter on. <br><br>"
            "1. Check resistance from plug lead G to un-anodized brew shelf.</b><br><br> "
            "<i> The millohm meter should not exceed 4.5 milliohms. </i><br><br>"
        )

        self.resistancelabel.setTextFormat(Qt.TextFormat.RichText)
        self.resistancelabel.setWordWrap(True)
        self.resistancelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.resistancelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.resistancelabel)

        self.resistancelabellayout.addWidget(scroll)
        layout.addLayout(self.resistancelabellayout)
        layout.addLayout(resistancetestbuttonlayout)
        try:
            self.resistancebeginbutton = QPushButton("Begin")
            self.resistancebeginbutton.setFixedWidth(200)
            self.resistancebeginbutton.clicked.connect(self.Resistance)
            resistancetestbuttonlayout.addWidget(self.resistancebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def Resistance(self):
            try:
                # STEP 1 — 4.5 mΩ
                if self.current_resistance_step == 0:
                    value, ok = NumericKeypadDialog.getValue(
                        self,
                        "Resistance Check",
                        "Please enter the resistance measurement in milliohms:",
                        decimals=3,
                        min_value=0.0,
                        max_value=100.0,
                    )

                    if ok:
                        result_line = f"Resistance Test {self.current_resistance_step + 1}: {value} mΩ"
                        if value <= 4.5:
                            result_line += "\tPASS"
                            self.step_status["step1_resistance_brewshelf"] = {
                                "status": "PASS",
                                "value": value
                            }
                            self.post_resistance_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step1_resistance_brewshelf"] = {
                                "status": "FAIL",
                                "value": value
                            }
                            self.post_resistance_snapshot()
                        self.insert_resistance_result(result_line)
                        print(f"User entered: {value} mΩ")
                        test1_results = value
                        self.resistance_results += f"Test {self.current_resistance_step + 1} Result: {value} mΩ\n"
                        if value <= 4.5:
                            self.resistance_passed[0] = True
                            self.resistance_failed[0] = False
                        else:
                            self.resistance_passed[0] = False
                            self.resistance_failed[0] = True

                        self.updateResistanceStep()
                        self.current_resistance_step += 1
                    return

                # STEP 2 — 5.12 mΩ
                elif self.current_resistance_step == 1:
                    value, ok = NumericKeypadDialog.getValue(
                        self,
                        "Resistance Check",
                        "Please enter the resistance measurement in milliohms:",
                        decimals=3,
                        min_value=0.0,
                        max_value=100.0,
                    )
                    test2_results = value
                    self.resistance_results += f"Test {self.current_resistance_step + 1} Result: {value} mOhms\n"
                    if ok:
                        result_line = f"Resistance Test {self.current_resistance_step + 1}: {value} mΩ"
                        if test2_results <= 5.12:
                            result_line += "\tPASS"
                            self.step_status["step2_resistance_hotplate"] = {
                                "status": "PASS",
                                "value": value
                            }
                            self.post_resistance_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step2_resistance_hotplate"] = {
                                "status": "FAIL",
                                "value": value
                            }
                            self.post_resistance_snapshot()
                        self.insert_resistance_result(result_line)
                        if value <= 5.12:
                            self.resistance_passed[1] = True
                            self.resistance_failed[1] = False
                        else:
                            self.resistance_passed[1] = False
                            self.resistance_failed[1] = True

                        self.updateResistanceStep()
                        self.current_resistance_step += 1
                    return

                # STEP 3 — 5.7 mΩ
                elif self.current_resistance_step == 2:
                    value, ok = NumericKeypadDialog.getValue(
                        self,
                        "Resistance Check",
                        "Please enter the resistance measurement in milliohms:",
                        decimals=3,
                        min_value=0.0,
                        max_value=100.0,
                    )
                    test3_results = value
                    self.resistance_results += f"Test {self.current_resistance_step + 1} Result: {value} mOhms\n"
                    print(self.resistance_results)
                    if ok:
                        result_line = f"Resistance Test {self.current_resistance_step + 1}: {value} mΩ"
                        if test3_results <= 5.7:
                            result_line += "\tPASS"
                            self.step_status["step3_resistance_faucet"] = {
                                "status": "PASS",
                                "value": value
                            }
                            self.post_resistance_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step3_resistance_faucet"] = {
                                "status": "FAIL",
                                "value": value
                            }
                            self.post_resistance_snapshot()
                        self.insert_resistance_result(result_line)
                        if value <= 5.7:
                            self.resistance_passed[2] = True
                            self.resistance_failed[2] = False
                            self.resistance_completed = True
                        else:
                            self.resistance_passed[2] = False
                            self.resistance_failed[2] = True

                        self.updateResistanceStep()
                        self.current_resistance_step += 1
                    return

                # Completed
                elif self.resistance_completed:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Test Completed!")
                    msg.setText("The Resistance test has been completed successfully.")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.exec()
                    self.updateResistanceStep()

            except Exception as e:
                print(f"Error: {e}")

    def updateResistanceStep(self):
        if self.resistance_passed[0] or self.resistance_failed[0]:
            self.resistancelabel.setText(
                "<b>2. If applicable, check the resistance from plug lead G to platen heater.</b><br><br>"
                "<i>The milliohm meter should not exceed 5.12 milliohms.</i><br><br>"
            )

            self.resistancebeginbutton.setText("Continue")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.Resistance)

        if self.resistance_passed[1] or self.resistance_failed[1]:
            self.resistancelabel.setText(
                "<b>3. Connect a resistance bridge between plug lead F and faucet.</b><br><br>"
                "<i>The milliohm meter should not exceed 5.7 milliohms.</i><br><br>"
            )

            self.resistancebeginbutton.setText("Continue")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.Resistance)

        if self.resistance_passed[2] or self.resistance_failed[2]:
            self.resistancelabel.setText(
                "<b>Resistance Test Completed!</b><br><br>"
                "<b>The Resistance Test has been completed successfully!</b><br><br>"
                "<b>Please Disconnect the IAS11003C plug from PP1 and turn off the milliohm meter.<br><br>"
            )
            self.resistancebeginbutton.setText("Results")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.ResistanceResults)

            self.resistancerestart = QPushButton("Restart", self)
            self.resistancerestart.clicked.connect(self.ResistanceRestart)
            self.resistancerestart.setFixedWidth(200)
            self.resistancetestbuttonlayout.addWidget(self.resistancerestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.resistancenext = QPushButton("Next", self)
            self.resistancenext.clicked.connect(self.ResistanceNext)
            self.resistancenext.setFixedWidth(200)
            self.resistancetestbuttonlayout.addWidget(self.resistancenext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def ResistanceNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def GetResistanceResults(self):
        return self.resistance_results

    def ResistanceTestPath(self, path):
        self.test_path = path

    def insert_resistance_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Resistance Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Resistance section not found.")
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

    def ResistanceRestart(self):
        print("Restarting Resistance Test")

    def ResistanceResults(self):
        print("Printing Resistance Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[Resistance] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

    def PostResistanceResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Resistance: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/resistance"
            r = requests.post(url, json=payload, timeout=5)
            print("Resistance POST status:", r.status_code)
            print("Resistance POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Resistance result: {e}")

    def post_resistance_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.resistance_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.resistance_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.resistance_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostResistanceResults(status=overall_status, data=data, notes=notes)


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