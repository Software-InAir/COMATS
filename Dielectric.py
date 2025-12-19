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


#-------------------------------------------------------- Dielectric Test
class DielectricTest(QWidget):


        def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None,  parent=None):
                super().__init__()

                self.instrument = instrument_worker
                self.tabs = tabs

                self.test_id: int | None = None
                self.api_base_url: str | None = None
                self.web = None

                #temp self.phase
                self.phase1read = 0
                self.phase2read = 0
                self.phase3read = 0

                self.dielectric_results = ""

                self.dielectric_passed = [False, False]
                self.dielectric_failed = [False, False]
                self.dielectric_completed = False
                self.current_dielectric_step = 0

                self.step_status = {}

                layout = QVBoxLayout()
                #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                #layout.addSpacerItem(spacer)

                ##layout.addStretch(1)
                
                dielectric_results = "Some test results."

                self.dielectriclabellayout = QHBoxLayout()

                self.dielectrictestbuttonlayout = QHBoxLayout()


                self.scroll = QScrollArea()
                self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


                self.scroll.setStyleSheet("""
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

                self.scroll.setMinimumHeight(500)
                self.scroll.setMaximumWidth(1200)
                self.scroll.setWidgetResizable(True)

                self.dielectriclabel = QLabel("""
                Begin by removing side panel<br><br><br>
                <b>1. Disconnect the P1 connector from J1 connector on circuit board.</b><br<br>
                <b>2. Install IAS11003B circular box connector into power input.</b><br><br>
                <i>Confirm test box leads are connected to hipot tester.</i><br><br>
                <b>2a. Install red and black test box jumpers from C to H.<br><br>
                Turn on the QuadTech Guardian 2510 Hipot Tester and press start.<br><br>
                The tester will increase the voltage of the Hi Pot test set in increments of 250 to 500 volts per second<br>
                until 1500 volts are applied across test connection and maintain the voltage at the 1500 volt level for 60 seconds.</b><br><br>
                Press Begin to continue.<br><br>
                """)

                self.dielectriclabel.setTextFormat(Qt.TextFormat.RichText)
                self.dielectriclabel.setWordWrap(True)
                self.dielectriclabel.setStyleSheet("""
                        font-size: 18px;
                        padding-top: 50px;
                        padding-left: 50px;
                        padding-right: 50px;
                        padding-bottom: 50px;
                        """)
                self.dielectriclabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.scroll.setWidget(self.dielectriclabel)


                self.dielectriclabellayout.addWidget(self.scroll)
                layout.addLayout(self.dielectriclabellayout)
                layout.addLayout(self.dielectrictestbuttonlayout)

                try:
                        self.dielectricbeginbutton = QPushButton("Begin", self)
                        self.dielectricbeginbutton.setFixedWidth(200)
                        self.dielectricbeginbutton.clicked.connect(self.Dielectric)
                        self.dielectrictestbuttonlayout.addWidget(self.dielectricbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

                except Exception as e:
                        print(f"Error while opening workorder: {e}")

                #-------------------------------------------------------------------- Phase Readings

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
                self.phase1reading.setText(f"{amps:.3f} A")

        @pyqtSlot(float)
        def show_current2(self, amps):
                self.phase2reading.setText(f"{amps:.3f} A")

        @pyqtSlot(float)
        def show_current3(self, amps):
                self.phase3reading.setText(f"{amps:.3f} A")

        def Dielectric(self):
                try:
                                        # STEP 1 — 4.5 mΩ
                        if self.current_dielectric_step == 0:
                                value, ok = NumericKeypadDialog.getValue(
                                        self,
                                        "Check Hi Pot Current",
                                        "Please enter the maximum current measured in milliamperes during the test period:",
                                        decimals=3,
                                        min_value=0.0,
                                        max_value=100.0,
                                )

                                if ok:
                                        result_line = f"Hi Pot Current Test {self.current_dielectric_step + 1}: {value} mA"
                                        if value <= 2:
                                                result_line += "\tPASS"
                                                self.step_status["step1_dielectric_hipot_current"] = {
                                                    "status": "PASS",
                                                    "value": value
                                                }
                                                self.post_dielectric_snapshot()
                                        else:
                                                result_line += "\tFAIL"
                                                self.step_status["step1_dielectric_hipot_current"] = {
                                                    "status": "FAIL",
                                                    "value": value
                                                }
                                                self.post_dielectric_snapshot()
                                        self.insert_dielectric_result(result_line)
                                        print(f"User entered: {value} mA")
                                        self.dielectric_results += f"Test {self.current_dielectric_step + 1} Result: {value} mA\n"
                                        self.dielectric_passed[0] = True
                                        self.dielectric_failed[0] = False
                                        self.current_dielectric_step += 1
                                        self.updateDielectricStep()



                        elif self.current_dielectric_step == 1:
                                value, ok = NumericKeypadDialog.getValue(
                                        self,
                                        "Check Megaohmmeter",
                                        "Please enter the resistance measured in megaohms:",
                                        decimals=3,
                                        min_value=0.0,
                                        max_value=100.0,
                                )

                                if ok:
                                        result_line = f"Megaohmmeter Resistance Test {self.current_dielectric_step + 1}: {value} mΩ"
                                        if value >= 2:
                                                result_line += "\tPASS"
                                                self.step_status["step2_dielectric_megaohm_resistance"] = {
                                                    "status": "PASS",
                                                    "value": value
                                                }
                                                self.post_dielectric_snapshot()
                                        else:
                                                result_line += "\tFAIL"
                                                self.step_status["step2_dielectric_megaohm_resistance"] = {
                                                    "status": "FAIL",
                                                    "value": value
                                                }
                                                self.post_dielectric_snapshot()
                                        self.insert_dielectric_result(result_line)
                                        print(f"User entered: {value} mΩ")
                                        self.dielectric_results += f"Test {self.current_dielectric_step + 1} Result: {value} mΩ\n"
                                        self.dielectric_passed[1] = True
                                        self.dielectric_failed[1] = False
                                        self.updateDielectricStep()


                        elif self.dielectric_completed:
                                msg1 = QMessageBox()
                                msg1.setWindowTitle("Test Completed!")
                                msg1.setText("The dielectric test has been completed successfully.")
                                #msg1.setIcon(QMessageBox.Icon.Information)

                                pass_button = msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)

                                msg1.exec()

                except Exception as e:
                        print(f"Error in: {e}")


        def updateDielectricStep(self):
                if self.dielectric_passed[0] or self.dielectric_failed[0]:
                        self.dielectriclabel.setText(
                                "<b>3. Connect QuadTech megohmmeter by connecting C and M jumpers on the test box.<br><br>"
                                "Set scale on megohmmeter to 500 volts and 100M.<br><br>"
                                "Turn megohmmeter power on.<br><br>"
                                "Flip switch to charge and then to measure.</b><br><br>"
                                "<i>The megohmmeter gauge must be greater than 2.</i><br><br>")

                        self.dielectricbeginbutton.setText("Continue")
                        self.dielectricbeginbutton.clicked.disconnect()
                        self.dielectricbeginbutton.clicked.connect(self.Dielectric)

                if self.dielectric_passed[1] or self.dielectric_failed[1] or self.current_dielectric_step > 1:
                        self.dielectriclabel.setText(
                                "<b>Test Complete.<br><br>"
                                "The Dielectric Test has been completed successfully!<br><br>"
                                "Please flip the megohmmeter switch to discharge and then power off.<br><br>"
                                "Disconnect IAS11003B circular box connector from the coffee maker.<br><br>"
                                "Reconnect P1 connector to J1 connector on circuit board.</b><br><br>")

                        self.dielectricbeginbutton.setText("Results")
                        self.dielectricbeginbutton.clicked.disconnect()
                        self.dielectricbeginbutton.clicked.connect(self.DielectricResults)

                        self.dielectricrestart = QPushButton("Restart", self)
                        self.dielectricrestart.clicked.connect(self.DielectricRestart)
                        self.dielectricrestart.setFixedWidth(200)
                        self.dielectrictestbuttonlayout.addWidget(self.dielectricrestart,
                                                                  alignment=Qt.AlignmentFlag.AlignCenter)

                        self.dielectricnext = QPushButton("Next", self)
                        self.dielectricnext.clicked.connect(self.DielectricNext)
                        self.dielectricnext.setFixedWidth(200)
                        self.dielectrictestbuttonlayout.addWidget(self.dielectricnext,
                                                                        alignment=Qt.AlignmentFlag.AlignCenter)

        def DielectricNext(self):
                current = self.tabs.currentIndex()
                self.tabs.setCurrentIndex(current + 1)

        def GetDielectricResults(self):
                return self.dielectric_results

        def DielectricTestPath(self, path):
                self.test_path = path

        def insert_dielectric_result(self, result_line: str):
                try:
                        with open(self.test_path, "r", encoding="utf-8") as file:
                                lines = file.readlines()

                        header_index = -1
                        found_line_index = -1
                        test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

                        # Step 1: Find the Resistance Test section
                        for i, line in enumerate(lines):
                                if line.strip() == ">>Dielectric Test<<":
                                        header_index = i
                                        break

                        if header_index == -1:
                                print("Dielectric section not found.")
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

        def DielectricRestart(self):

                try:
                        print("Restarting Dielectric Test")

                        # ---------- State reset ----------
                        self.dielectric_results = ""
                        self.dielectric_passed = [False] * len(self.dielectric_passed)
                        self.dielectric_failed = [False] * len(self.dielectric_failed)
                        self.dielectric_completed = False
                        self.current_dielectric_step = 0
                        self.step_status = {}

                        # ---------- Restore instructions ----------
                        self.dielectriclabel.setText(
                                """
                Begin by removing side panel<br><br><br>
                <b>1. Disconnect the P1 connector from J1 connector on circuit board.</b><br<br>
                <b>2. Install IAS11003B circular box connector into power input.</b><br><br>
                <i>Confirm test box leads are connected to hipot tester.</i><br><br>
                <b>2a. Install red and black test box jumpers from C to H.<br><br>
                Turn on the QuadTech Guardian 2510 Hipot Tester and press start.<br><br>
                The tester will increase the voltage of the Hi Pot test set in increments of 250 to 500 volts per second<br>
                until 1500 volts are applied across test connection and maintain the voltage at the 1500 volt level for 60 seconds.</b><br><br>
                Press Begin to continue.<br><br>
                """
                        )

                        # ---------- Remove completion buttons ----------
                        if hasattr(self, "dielectricrestart") and self.dielectricrestart:
                                self.dielectrictestbuttonlayout.removeWidget(self.dielectricrestart)
                                self.dielectricrestart.deleteLater()
                                self.dielectricrestart = None

                        if hasattr(self, "dielectricnext") and self.dielectricnext:
                                self.dielectrictestbuttonlayout.removeWidget(self.dielectricnext)
                                self.dielectricnext.deleteLater()
                                self.dielectricnext = None

                        # ---------- Restore Begin button ----------
                        self.dielectricbeginbutton.setText("Begin")
                        try:
                                self.dielectricbeginbutton.clicked.disconnect()
                        except TypeError:
                                pass
                        self.dielectricbeginbutton.clicked.connect(self.Dielectric)

                except Exception as e:
                        print(f"Error restarting Dielectric Test: {e}")

        def DielectricResults(self):
                print("Printing Dielectric Test Results")

        def set_test_context(self, test_id: int, api_base_url: str):
            self.test_id = test_id
            self.api_base_url = api_base_url.rstrip("/")
            print(f"[Dielectric] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

            self.SubtestsCompleted()

        def PostDielectricResults(self, status: str, data: dict, notes: str):
            if self.test_id is None or self.api_base_url is None:
                print("Dielectric: Test Context not set; skipping Post")
                return

            payload = {
                "status": status,
                "data": data,
                "notes": notes,
            }

            try:
                url = f"{self.api_base_url}/tests/{self.test_id}/subtests/dielectric"
                r = requests.post(url, json=payload, timeout=5)
                print("Dielectric POST status:", r.status_code)
                print("Dielectric POST body:", repr(r.text))
                r.raise_for_status()
            except Exception as e:
                print(f"Error posting Dielectric result: {e}")

        def post_dielectric_snapshot(self):
            """
            Compute an overall status from what we know so far and POST to the server.
            This can be called after each step so partial progress is saved.
            """
            # Overall status logic:
            # - If test not completed yet, call it "INCOMPLETE"
            # - If completed, PASS only if all tracked steps passed
            if not self.dielectric_completed:
                overall_status = "INCOMPLETE"
            else:
                overall_status = "PASS" if all(self.dielectric_passed) else "FAIL"

            data = {
                "steps": self.step_status,
                "completed": self.dielectric_completed,
            }

            notes = ""  # or derive something from failures if you want

            self.PostDielectricResults(status=overall_status, data=data, notes=notes)

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

        def SubtestsCompleted(self):
                if self.test_id is None or self.api_base_url is None:
                        return

                try:
                        url = f"{self.api_base_url}/tests/{self.test_id}/subtests/dielectric"
                        r = requests.get(url, timeout=3)

                        if r.status_code == 404:
                                print("this")
                                return  # not run yet

                        r.raise_for_status()
                        payload = r.json()

                        status = payload.get("status", "").upper()
                        print(status)

                        if status in ("PASS", "FAIL", "COMPLETED"):
                                # Fully done → jump to completed screen
                                self.current_dielectric_step = 2
                                print(f"Current step: {self.current_dielectric_step}")
                                self.updateDielectricStep()

                        elif status == "INCOMPLETE":
                                steps = payload.get("data", {}).get("steps", {})
                                # Resume at "next" step index
                                self.current_dielectric_step = len(steps)
                                print(f"Current step: {self.current_dielectric_step}")
                                self.updateDielectricStep()
                                return

                        self.updateDielectricStep()

                except Exception as e:
                        print(f"[Dielectric] sync_completed_from_db failed: {e}")
