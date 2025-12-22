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



#------------------------------------------------------- AmbientTemperature Check

class AmbientTemperatureTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None,  parent=None):
        super().__init__()
        self.setMinimumSize(1200, 600)
        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.ambienttemp_results = ""
        self.ambienttemp_passed = [False, False, False]
        self.ambienttemp_failed = [False, False, False]
        self.ambienttemp_completed = False
        self.current_ambienttemp_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.ambientlabellayout = QHBoxLayout()

        self.ambienttemptestbuttonlayout = QHBoxLayout()

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

        self.ambienttemplabel = QLabel(
            "<b>1. Using the wall thermometer, measure the temperature in the adjacent"
            " area of the test environment. </b><br><br>"
            "<i>The temperature should be between 70° F (21° C) and 85° F (29° C).</i><br><br>"
        )

        self.ambienttemplabel.setTextFormat(Qt.TextFormat.RichText)
        self.ambienttemplabel.setWordWrap(True)
        self.ambienttemplabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.ambienttemplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.ambienttemplabel)

        self.ambientlabellayout.addWidget(scroll)
        layout.addLayout(self.ambientlabellayout)
        layout.addLayout(self.ambienttemptestbuttonlayout)
        try:
            self.ambienttempbeginbutton = QPushButton("Begin")
            self.ambienttempbeginbutton.setFixedWidth(200)
            self.ambienttempbeginbutton.clicked.connect(self.AmbientTemperature)
            self.ambienttemptestbuttonlayout.addWidget(self.ambienttempbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def AmbientTemperature(self):
        try:
            # STEP 1 — 4.5 mΩ
            if self.current_ambienttemp_step == 0:
                value, ok = NumericKeypadDialog.getValue(
                    self,
                    "Check Temperature",
                    "Please enter the temperature displayed on provided thermometer:",
                    decimals=1,
                    initial=0,
                    min_value=0.0,
                    max_value=300.0,

                )

                if ok:
                    if value < 60:
                        tempsystem = "°C"
                    else:
                        tempsystem = "°F"
                    result_line = f"Ambient Temperature Test {self.current_ambienttemp_step + 1}: {value}{tempsystem} "
                    if tempsystem == "°F":
                        if value >= 70 and value <=85:
                            result_line += "\tPASS"
                            self.step_status["step1_ambienttemp_temp"] = {
                                "status": "PASS",
                                "value": value
                            }
                            self.post_ambienttemp_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step1_ambienttemp_temp"] = {
                                "status": "FAIL",
                                "value": value
                            }
                            self.post_ambienttemp_snapshot()
                    elif tempsystem == "°C":
                        if value >= 21 and value <=29:
                            result_line += "\tPASS"
                            self.step_status["step1_ambienttemp_temp"] = {
                                "status": "PASS",
                                "value": value
                            }
                            self.post_ambienttemp_snapshot()
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step1_ambienttemp_temp"] = {
                                "status": "FAIL",
                                "value": value
                            }
                            self.post_ambienttemp_snapshot()
                    self.insert_ambienttemp_result(result_line)
                    print(f"User entered: {value} mA")
                    self.ambienttemp_results += f"Test {self.current_ambienttemp_step + 1} Result: {value}\n"
                    self.ambienttemp_passed[0] = True
                    self.ambienttemp_failed[0] = False
                    self.ambienttemp_completed = True
                    self.current_ambienttemp_step += 1
                    self.updateAmbientTempStep()
                    self.post_ambienttemp_snapshot()

        except Exception as e:
            print(f"Error: {e}")



    def updateAmbientTempStep(self):


        if self.ambienttemp_passed[0] or self.ambienttemp_failed[0] or self.current_ambienttemp_step > 0:
            self.ambienttemplabel.setText(
                "<b>Test Complete.</b><br><br>"
                "<b>The Ambient Temperature Test has been completed successfully!<br><br>"
            )
            self.ambienttempbeginbutton.setText("Results")
            self.ambienttempbeginbutton.clicked.disconnect()
            self.ambienttempbeginbutton.clicked.connect(self.AmbientTemperatureResults)

            self.ambienttemprestart = QPushButton("Restart", self)
            self.ambienttemprestart.clicked.connect(self.AmbientTemperatureRestart)
            self.ambienttemprestart.setFixedWidth(200)
            self.ambienttemptestbuttonlayout.addWidget(self.ambienttemprestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.ambienttempnext = QPushButton("Next", self)
            self.ambienttempnext.clicked.connect(self.AmbientTempNext)
            self.ambienttempnext.setFixedWidth(200)
            self.ambienttemptestbuttonlayout.addWidget(self.ambienttempnext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def AmbientTempNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def AmbientTempResults(self):
        print("Printing AmbientTemp Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/ambienttemp"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "AmbientTemp has not been run yet.")
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
            "step1_ambienttemp_temp": "Ambient Temperature Measurement:",
        }

        ordered_keys = [
            "step1_ambienttemp_temp",
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
        report_lines.append("Ambient Temperature Test")

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
        text = "<h2>Ambient Temp Results</h2>"
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
        win.setWindowTitle("Ambient Temp Results")
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

        self._ambienttemp_results_window = win

    def AmbientTempTestPath(self, path):
        self.test_path = path

    def insert_ambienttemp_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Ambient Temperature Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Ambient Temperature section not found.")
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

    def AmbientTemperatureRestart(self):
        try:
            print("Restarting AmbientTemperature Test")

            # ---------------- State reset ----------------
            self.ambienttemp_results = ""
            self.ambienttemp_passed = [False, False, False]
            self.ambienttemp_failed = [False, False, False]
            self.ambienttemp_completed = False
            self.current_ambienttemp_step = 0
            self.step_status = {}

            # ---------------- UI reset ----------------
            # Restore original instruction text
            self.ambienttemplabel.setText(
                "<b>1. Using the wall thermometer, measure the temperature in the adjacent"
                " area of the test environment. </b><br><br>"
                "<i>The temperature should be between 70° F (21° C) and 85° F (29° C).</i><br><br>"
            )

            # Remove "complete screen" buttons if they exist
            if hasattr(self, "ambienttemprestart") and self.ambienttemprestart is not None:
                self.ambienttemptestbuttonlayout.removeWidget(self.ambienttemprestart)
                self.ambienttemprestart.deleteLater()
                self.ambienttemprestart = None

            if hasattr(self, "ambienttempnext") and self.ambienttempnext is not None:
                self.ambienttemptestbuttonlayout.removeWidget(self.ambienttempnext)
                self.ambienttempnext.deleteLater()
                self.ambienttempnext = None

            # Restore Begin button to original behavior
            self.ambienttempbeginbutton.setText("Begin")
            try:
                self.ambienttempbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.ambienttempbeginbutton.clicked.connect(self.AmbientTemperature)

        except Exception as e:
            print(f"Error restarting AmbientTemperature Test: {e}")

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

    def AmbientTemperatureResults(self):
        print("Printing AmbientTemp Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/ambienttemp"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "AmbientTemp has not been run yet.")
                return

            r.raise_for_status()
            result = r.json()

        except Exception as e:
            QMessageBox.critical(self, "API Error", str(e))
            return

        # ---------- Build display ----------
        status = result.get("status", "UNKNOWN")
        notes = result.get("notes", "")
        data = result.get("data", {}) or {}
        failures = data.get("failures", []) or []

        text = "<h2>AmbientTemp Results</h2>"
        text += f"<b>Status:</b> {status}<br><br>"

        if failures:
            text += "<b>Failures:</b><ul>"
            for f in failures:
                text += f"<li>{f}</li>"
            text += "</ul><br>"
        else:
            text += "<b>Failures:</b> None<br><br>"

        if notes:
            text += f"<b>Notes:</b><br>{notes}<br>"

        # Optional: dump remaining data keys (helps during early bring-up)
        extra_keys = [k for k in data.keys() if k != "failures"]
        if extra_keys:
            text += "<br><b>Data:</b><ul>"
            for k in extra_keys:
                text += f"<li><b>{k}</b>: {data.get(k)!r}</li>"
            text += "</ul>"

        # ---------- Show window ----------
        win = QMainWindow(self)
        win.setWindowTitle("AmbientTemp Results")
        win.resize(700, 500)

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

        # keep reference so GC doesn't nuke it
        self._ambienttemp_results_window = win

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[AmbientTemperature] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

    def PostAmbientTemperatureResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Ambient Temperature: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/ambienttemp"
            r = requests.post(url, json=payload, timeout=5)
            print("Ambient Temperature POST status:", r.status_code)
            print("Ambient Temperature POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Ambient Temperature result: {e}")

    def post_ambienttemp_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.ambienttemp_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.ambienttemp_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.ambienttemp_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostAmbientTemperatureResults(status=overall_status, data=data, notes=notes)

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
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/ambienttemp"
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
                self.current_ambienttemp_step = 2
                print(f"Current step: {self.current_ambienttemp_step}")
                self.updateAmbientTempStep()

            elif status == "INCOMPLETE":
                steps = payload.get("data", {}).get("steps", {})
                # Resume at "next" step index
                self.current_ambienttemp_step = len(steps)
                print(f"Current step: {self.current_ambienttemp_step}")
                self.updateAmbientTempStep()
                return

            self.updateAmbientTempStep()

        except Exception as e:
            print(f"[AmbientTemp] sync_completed_from_db failed: {e}")