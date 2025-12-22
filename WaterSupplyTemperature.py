from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog, QComboBox
)

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QUrl

from InstrumentWorker import InstrumentWorker

from NumPad import NumericKeypadDialog

import requests
import datetime
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



#------------------------------------------------------- WaterTemp Check

class WaterTempTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.watertemp_results = ""
        self.watertemp_passed = [False, False, False]
        self.watertemp_failed = [False, False, False]
        self.watertemp_completed = False

        self.current_watertemp_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.watersupplylabellayout = QHBoxLayout()
        self.watertemptestbuttonlayout = QHBoxLayout()

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

        self.watertemplabel = QLabel(
            "<b>1. If water supply is connected to the Beverage Maker, "
                "disconnect water supply from the Beverage Maker. <br><br>"
                "Open V9 for 10 seconds to flow water through TM2. <br><br>"
                "2. Measure the temperature of the water from the water "
                "supply by reading thermometer TM2. </b><br><br>"
            "<i> The temperature of the water should be 62° F (17° C) to 72° F (22° C). </i><br><br>"
        )

        self.watertemplabel.setTextFormat(Qt.TextFormat.RichText)
        self.watertemplabel.setWordWrap(True)
        self.watertemplabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.watertemplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.watertemplabel)

        self.watersupplylabellayout.addWidget(scroll)
        layout.addLayout(self.watersupplylabellayout)
        layout.addLayout(self.watertemptestbuttonlayout)
        try:
            self.watertempbeginbutton = QPushButton("Begin")
            self.watertempbeginbutton.setFixedWidth(200)
            self.watertempbeginbutton.clicked.connect(self.WaterTemp)
            self.watertemptestbuttonlayout.addWidget(self.watertempbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        self.phase1reading.setText(f"{amps:.3f} A")

    @pyqtSlot(float)
    def show_current2(self, amps):
        self.phase2reading.setText(f"{amps:.3f} A")

    @pyqtSlot(float)
    def show_current3(self, amps):
        self.phase3reading.setText(f"{amps:.3f} A")

    def WaterTemp(self):
        try:
            # STEP 1 — 4.5 mΩ
            if self.current_watertemp_step == 0:
                value, ok = NumericKeypadDialog.getValue(
                    self,
                    "Check Temperature",
                    "Please enter the temperature displayed on provided thermometer:",
                    decimals=1,
                    min_value=0.0,
                    max_value=300.0,
                )

                if ok:
                    if value < 60:
                        tempsystem = "C"
                    else:
                        tempsystem = "F"
                    result_line = f"Water Supply Temperature Test {self.current_watertemp_step + 1}: {value}°{tempsystem} "
                    if tempsystem == "F":
                        if value >= 62 and value <=72:
                            result_line += "\tPASS"
                            self.step_status["step1_watertemp_temp"] = {
                                "status": "PASS",
                                "value": value
                            }
                            self.post_watertemp_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step1_watertemp_temp"] = {
                                "status": "FAIL",
                                "value": value
                            }
                            self.post_watertemp_snapshot()
                    elif tempsystem == "C":
                        if value >= 17 and value <=22:
                            result_line += "\tPASS"
                            self.step_status["step1_watertemp_temp"] = {
                                "status": "PASS",
                                "value": value
                            }
                            self.post_watertemp_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step1_watertemp_temp"] = {
                                "status": "FAIL",
                                "value": value
                            }
                            self.post_watertemp_snapshot()
                    self.insert_watertemp_result(result_line)
                    print(f"User entered: {value} mA")
                    self.watertemp_results += f"Test {self.current_watertemp_step + 1} Result: {value} mA\n"
                    self.watertemp_passed[0] = True
                    self.watertemp_failed[0] = False
                    self.watertemp_completed = True
                    self.post_watertemp_snapshot()
                    self.current_watertemp_step += 1
                    self.updateWaterTempStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateWaterTempStep(self):
        if self.watertemp_passed[0] or self.watertemp_failed[0] or self.current_watertemp_step > 0:
            self.watertemplabel.setText(
                "<b>Test Complete.</b><br><br>"
                "<b>The Water Supply Temperature test has been completed successfully.</b><br><br>"
            )

            self.watertempbeginbutton.setText("Results")
            self.watertempbeginbutton.clicked.disconnect()
            self.watertempbeginbutton.clicked.connect(self.WaterTempResults)

            self.watertemprestart = QPushButton("Restart", self)
            self.watertemprestart.clicked.connect(self.WaterTempRestart)
            self.watertemprestart.setFixedWidth(200)
            self.watertemptestbuttonlayout.addWidget(self.watertemprestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.watertempnext = QPushButton("Next", self)
            self.watertempnext.clicked.connect(self.WaterTempNext)
            self.watertempnext.setFixedWidth(200)
            self.watertemptestbuttonlayout.addWidget(self.watertempnext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def WaterTempNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def _show_results_window(self, title: str, html: str, w: int = 750, h: int = 520,
                             attr_name: str = "_results_window"):
        win = QMainWindow(self)
        win.setWindowTitle(title)
        win.resize(w, h)

        label = QLabel(html)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setAlignment(Qt.AlignmentFlag.AlignTop)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(label)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(win.close)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        win.setCentralWidget(container)
        win.show()

        # keep reference so GC doesn't nuke it
        setattr(self, attr_name, win)

    def _fetch_subtest_result(self, subtest_slug: str):
        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return None

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/{subtest_slug}"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", f"{subtest_slug} has not been run yet.")
                return None

            r.raise_for_status()
            return r.json()

        except Exception as e:
            QMessageBox.critical(self, "API Error", str(e))
            return None

    def _build_results_html(self, heading: str, result: dict, report_block: str | None = None) -> str:
        status = (result.get("status", "UNKNOWN") or "UNKNOWN").upper()
        notes = result.get("notes", "") or ""
        data = result.get("data", {}) or {}
        failures = data.get("failures", []) or []

        html = f"<h2>{heading}</h2>"
        html += f"<b>Status:</b> {status}<br><br>"

        if failures:
            html += "<b>Failures:</b><ul>"
            for f in failures:
                html += f"<li>{f}</li>"
            html += "</ul><br>"
        else:
            html += "<b>Failures:</b> None<br><br>"

        if report_block:
            html += (
                "<div style=\"font-family: Consolas, 'Courier New', monospace; "
                "font-size: 14px; white-space: pre; "
                "padding: 10px; border: 1px solid #ddd; background: #f7f7f7;\">"
                f"{report_block}"
                "</div><br>"
            )

        if notes:
            html += f"<b>Notes:</b><br>{notes}<br>"

        # Optional: if you still want *some* data shown, show it cleanly:
        # (no repr dumps, no raw dicts)
        # Example: completed flag
        if "completed" in data:
            html += f"<br><b>Completed:</b> {'Yes' if bool(data.get('completed')) else 'No'}<br>"

        return html

    def WaterSupplyTempResults(self):
        print("Printing WaterSupplyTemp Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/watersupplytemp"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "WaterSupplyTemp has not been run yet.")
                return

            r.raise_for_status()
            result = r.json()

        except Exception as e:
            QMessageBox.critical(self, "API Error", str(e))
            return

        # ---------- Parse ----------
        status = (result.get("status", "UNKNOWN") or "UNKNOWN").upper()
        notes = result.get("notes", "") or ""
        data = result.get("data", {}) or {}
        failures = data.get("failures", []) or []
        completed = bool(data.get("completed", False))
        steps = data.get("steps", {}) or {}

        # Friendly labels that match your text file
        step_labels = {
            "step1_watertemp_temp": "Water Supply Temperature Measurement:",
        }

        ordered_keys = [
            "step1_watertemp_temp",
        ]

        def unpack_step(step_obj):
            # supports: "PASS" or {"status":"PASS","value":0.0}
            if isinstance(step_obj, str):
                return step_obj.upper(), None
            if isinstance(step_obj, dict):
                st = (step_obj.get("status") or "UNKNOWN").upper()
                val = step_obj.get("value", None)
                return st, val
            return "UNKNOWN", None

        # Build the "passed tests" block (always show it)
        col_width = 68
        report_lines = []
        report_lines.append("Water Supply Temperature Test")

        for k in ordered_keys:
            label = step_labels.get(k, f"{k}:")
            raw = steps.get(k)

            # If step isn't present yet, show blank status
            if raw is None:
                report_lines.append(label.ljust(col_width))
                continue

            st, val = unpack_step(raw)

            if val is not None:
                left = f"{label} {val}"
            else:
                left = label

            report_lines.append(left.ljust(col_width) + (st if st != "UNKNOWN" else ""))

        report_pre = "\n".join(report_lines)

        # ---------- Build display ----------
        text = "<h2>Water Supply Temperature Results</h2>"
        text += f"<b>Status:</b> {status}<br><br>"

        if failures:
            text += "<b>Failures:</b><ul>"
            for f in failures:
                text += f"<li>{f}</li>"
            text += "</ul><br>"
        else:
            text += "<b>Failures:</b> None<br><br>"

        text += f"<b>Completed:</b> {'Yes' if completed else 'No'}<br><br>"

        # ✅ Always show what it passed (and any missing lines)
        text += (
            "<div style=\"font-family: Consolas, 'Courier New', monospace; "
            "font-size: 14px; white-space: pre; "
            "padding: 10px; border: 1px solid #ddd; background: #f7f7f7;\">"
            f"{report_pre}"
            "</div><br>"
        )

        if notes:
            text += f"<b>Notes:</b><br>{notes}<br>"

        # ---------- Show window ----------
        win = QMainWindow(self)
        win.setWindowTitle("Water Supply Temperature Results")
        win.resize(750, 520)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setAlignment(Qt.AlignmentFlag.AlignTop)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(label)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(win.close)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

        win.setCentralWidget(container)
        win.show()

        self._watersupplytemp_results_window = win

    def WaterTempTestPath(self, path):
        self.test_path = path

    def insert_watertemp_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Water Supply Temperature Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Water Supply Temperature section not found.")
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

    def WaterTempRestart(self):
        try:
            print("Restarting WaterTemp Test")

            # ---------- State reset ----------
            self.watertemp_results = ""
            self.watertemp_passed = [False] * len(self.watertemp_passed)
            self.watertemp_failed = [False] * len(self.watertemp_failed)
            self.watertemp_completed = False
            self.current_watertemp_step = 0
            self.step_status = {}

            # ---------- Restore instructions ----------
            self.watertemplabel.setText(
                "<b>1. If water supply is connected to the Beverage Maker, "
                "disconnect water supply from the Beverage Maker. <br><br>"
                "Open V9 for 10 seconds to flow water through TM2. <br><br>"
                "2. Measure the temperature of the water from the water "
                "supply by reading thermometer TM2. </b><br><br>"
            "<i> The temperature of the water should be 62° F (17° C) to 72° F (22° C). </i><br><br>"
            )

            # ---------- Remove completion buttons ----------
            if hasattr(self, "watertemprestart") and self.watertemprestart:
                self.watertemptestbuttonlayout.removeWidget(self.watertemprestart)
                self.watertemprestart.deleteLater()
                self.watertemprestart = None

            if hasattr(self, "watertempnext") and self.watertempnext:
                self.watertemptestbuttonlayout.removeWidget(self.watertempnext)
                self.watertempnext.deleteLater()
                self.watertempnext = None

            # ---------- Restore Begin button ----------
            self.watertempbeginbutton.setText("Begin")
            try:
                self.watertempbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.watertempbeginbutton.clicked.connect(self.WaterTemp)

        except Exception as e:
            print(f"Error restarting WaterTemp Test: {e}")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[WaterTemp] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

    def PostWaterTempResults(self, status: str,data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Water Temp: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }


        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/watertemp"
            r = requests.post(url, json=payload, timeout=5)
            print("Water Temp POST status:", r.status_code)
            print("Water Temp POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Water Temp result: {e}")



    def post_watertemp_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed

        if not self.watertemp_completed:
            overall_status = "INCOMPLETE"

        if self.watertemp_completed:
            overall_status = "PASS" if all(self.watertemp_passed) else "FAIL"

        data = {
            "status": overall_status,
            "steps": self.step_status,
        }

        notes = ""  # or derive something from failures if you want

        self.PostWaterTempResults(status=overall_status, data=data, notes=notes)

        if self.watertemp_completed:
            # You said you want this field in the parent JSON:
            #   "status": "completed"
            self.PostParentTestStatus(status="completed", completed=True)


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
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/watertemp"
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
                self.current_watertemp_step = 1
                print(f"Current step: {self.current_watertemp_step}")
                self.updateWaterTempStep()

            elif status == "INCOMPLETE":
                steps = payload.get("data", {}).get("steps", {})
                # Resume at "next" step index
                self.current_watertemp_step = len(steps)
                print(f"Current step: {self.current_watertemp_step}")
                self.updateWaterTempStep()
                return

            self.updateWaterTempStep()

        except Exception as e:
            print(f"[WaterTemp] sync_completed_from_db failed: {e}")






