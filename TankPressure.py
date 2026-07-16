from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog, QComboBox, QDialog
)

from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal, QUrl, QTimer

from InstrumentWorker import InstrumentWorker

from NumPad import NumericKeypadDialog

import requests
import subprocess
import platform
import os
import sys

from pathlib import Path
from paths import resource_path

class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- TankPressure Check

class TankPressureTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.tankpressure_results = ""
        self.tankpressure_passed = [False, False, False]
        self.tankpressure_failed = [False, False, False]
        self.tankpressure_completed = False
        self.current_tankpressure_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phaseAread = 0
        self.phaseBread = 0
        self.phaseCread = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.tankpressurelabellayout = QHBoxLayout()
        self.tankpressuretestbuttonlayout = QHBoxLayout()

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

        self.tankpressurelabel = QLabel(
            "<b>Remove plastic drain tube from clip behind server.<br><br>"
            "Use 11/16 wrench to remove pressure relief valve.<br><br>"
            "Use a 7/16 wrench to secure 1/8 inch NPT plug wrapped with teflon tape.<br><br>"
            "1. Replace the pressure relief valve with a 1/8 inch NPT plug prior to " 
            "testing.<br><br>"
            "Close V10 then turn V8 vertical. <br><br>"
            "2. Connect the Beverage Maker to water supply and then open V10.<br><br>"
            "3. Let tank fill with water. Flow meter will go to zero when tank is full.<br><br>" 
            "4. Adjust water pressure by rotating V7 clockwise until PG2 reads 130 psig (8.96 barg).<br><br>"
            "Hold for a minimum of 5 minutes.<br><br>"
            "Inspect tank for leaks.<br><br>"
            "<i>No leaks are allowed.</i><br><br>"
        )

        self.tankpressurelabel.setTextFormat(Qt.TextFormat.RichText)
        self.tankpressurelabel.setWordWrap(True)
        self.tankpressurelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.tankpressurelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.tankpressurelabel)

        self.tankpressurelabellayout.addWidget(scroll)
        layout.addLayout(self.tankpressurelabellayout)
        layout.addLayout(self.tankpressuretestbuttonlayout)
        try:
            self.tankpressurebeginbutton = QPushButton("Begin")
            self.tankpressurebeginbutton.setFixedWidth(200)
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)
            self.tankpressuretestbuttonlayout.addWidget(self.tankpressurebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

        # -------------------------------------------------------------------- Phase Readings

        self.bottomToolbar = QHBoxLayout()

        self.phaselayout = QVBoxLayout()

        self.resources = QPushButton("Resources")
        self.resources.setFixedWidth(200)
        self.resources.clicked.connect(self.OnResources)
        self.bottomToolbar.addWidget(self.resources)

        self.timer_button = QPushButton("Timer")
        self.timer_button.setFixedWidth(150)
        self.timer_button.clicked.connect(self.show_timer_popup)
        self.bottomToolbar.addWidget(self.timer_button)

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.bottomToolbar.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.bottomToolbar.addSpacerItem(spacer2)

        self.phaseAlayout = QHBoxLayout()
        self.phaseA = QLabel("Phase A:")
        self.phaseA.setStyleSheet("""
                                                font: 18px;
                                                """)
        self.phaseAlayout.addWidget(self.phaseA)

        self.phaseAreading = QLabel(f"{self.phaseAread}")
        self.phaseAreading.setStyleSheet("""
                                        font: 18px;
                                        """)
        self.phaseAlayout.addWidget(self.phaseAreading)

        self.phaselayout.addLayout(self.phaseAlayout)

        self.phaseBlayout = QHBoxLayout()

        self.phaseB = QLabel("Phase B:")
        self.phaseB.setStyleSheet("""
                                                        font: 18px;
                                                        """)
        self.phaseBlayout.addWidget(self.phaseB)

        self.phaseBreading = QLabel(f"{self.phaseBread}")
        self.phaseBreading.setStyleSheet("""
                                                font: 18px;
                                                """)
        self.phaseBlayout.addWidget(self.phaseBreading)

        self.phaselayout.addLayout(self.phaseBlayout)

        self.phaseClayout = QHBoxLayout()

        self.phaseC = QLabel("Phase C:")
        self.phaseC.setStyleSheet("""
                                                        font: 18px;
                                                        """)
        self.phaseClayout.addWidget(self.phaseC)

        self.phaseCreading = QLabel(f"{self.phaseCread}")
        self.phaseCreading.setStyleSheet("""
                                                font: 18px;
                                                """)
        self.phaseClayout.addWidget(self.phaseCreading)

        self.phaselayout.addLayout(self.phaseClayout)

        self.bottomToolbar.addLayout(self.phaselayout)

        layout.addLayout(self.bottomToolbar)

        self.setLayout(layout)

        if self.instrument is not None:
            self.instrument.ch1.connect(self.show_current1)
            self.instrument.ch2.connect(self.show_current2)
            self.instrument.ch3.connect(self.show_current3)

    @pyqtSlot(float)
    def show_current1(self, amps):
        self.phaseAreading.setText(f"{amps:.3f} A")

    @pyqtSlot(float)
    def show_current2(self, amps):
        self.phaseBreading.setText(f"{amps:.3f} A")

    @pyqtSlot(float)
    def show_current3(self, amps):
        self.phaseCreading.setText(f"{amps:.3f} A")

    def TankPressure(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_tankpressure_step == 0:
                msg1.setWindowTitle("Check Tank")
                msg1.setText("No tank leaks found.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Leak Check Test: "
                    result_line += "\tPASS"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step1_tankpressure_leak"] = {
                        "status": "PASS",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[0] = True
                    self.tankpressure_failed[0] = False
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Leak Check Test: "
                    result_line += "\tFAIL"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step1_tankpressure_leak"] = {
                        "status": "FAIL",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[0] = False
                    self.tankpressure_failed[0] = True
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1

            elif self.current_tankpressure_step == 1:
                msg1.setWindowTitle("Check Vent Valve")
                msg1.setText("Vent Valve operates as instructed.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Vent Valve Test: "
                    result_line += "\tPASS"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step2_tankpressure_ventvalve"] = {
                        "status": "PASS",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[1] = True
                    self.tankpressure_failed[1] = False
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Vent Valve Test: "
                    result_line += "\tFAIL"
                    self.insert_tankpressure_result(result_line)
                    self.step_status["step2_tankpressure_ventvalve"] = {
                        "status": "FAIL",
                    }
                    self.post_tankpressure_snapshot()
                    self.tankpressure_passed[1] = False
                    self.tankpressure_failed[1] = True
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_tankpressure_step == 2:
                value, ok = NumericKeypadDialog.getValue(
                    self,
                    "Check Pressure",
                    "Please enter the pressure displayed on PG:",
                    decimals=2,
                    min_value=0.0,
                    max_value=100.0,
                )

                if ok:

                    result_line = f"Tank Pressure Test {self.current_tankpressure_step + 1}: {value} PSI "
                    if value < 30:
                        result_line += "\tPASS"
                        self.step_status["step3_tankpressure_pressure"] = {
                            "status": "PASS",
                            "value": value
                        }
                        self.tankpressure_passed[2] = True
                        self.tankpressure_failed[2] = False
                        self.post_tankpressure_snapshot()
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step3_tankpressure_pressure"] = {
                            "status": "FAIL",
                            "value": value
                        }
                        self.tankpressure_passed[2] = False
                        self.tankpressure_failed[2] = True
                        self.post_tankpressure_snapshot()

                    self.insert_tankpressure_result(result_line)
                    print(f"User entered: {value} PSI")
                    self.tankpressure_results += f"Test {self.current_tankpressure_step + 1} Result: {value}\n"
                    self.tankpressure_completed = True
                    self.post_tankpressure_snapshot()
                    self.current_tankpressure_step += 1
                    self.updateTankPressureStep()



            # Completed
            elif self.tankpressure_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The TankPressure test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateTankPressureStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateTankPressureStep(self):
        if self.tankpressure_passed[0] or self.tankpressure_failed[0]:
            self.tankpressurelabel.setText(
                "Rotate V7 counterclockwise until PG2 reads below 70 psi.<br><br>"
                "Open V9 periodically to verify pressure is below 70 psi.<br><br>"
                "Close V10.<br><br>"
                "5. Release pressure by opening V11 then remove plug.<br><br>"
                "6. Put pressure relief valve back into the tank using thread seal tape.<br>"
                "Insert plastic drain tube back into original place.<br>"
                "Tighten with 11/16 wrench.<br>"
                "Close V11 and open V10.7.<br><br>"
                "Gradually increase the water pressure to the tank.<br>"
                "Slowly rotate V7 clockwise while watching PG2.<br><br>"
                "<i>The relief valve should remain closed at pressures below 75 psig (5.17 barg).</i><br><br>"
                "Continue to increase pressure ensuring the valve is fully open prior to or at 100 psig (6.89 barg).<br><br>"
                "8. Disconnect water supply by turning V10 off and drain the Beverage Maker by opening V11.<br><br>"
                "<i>Ensure that vent valve operates correctly as described.</i><br><br>"
            )

            self.tankpressurebeginbutton.setText("Continue")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)


        if self.tankpressure_passed[1] or self.tankpressure_failed[1]:
            self.tankpressurelabel.setText(
                "Turn V7 counterclockwise to return pressure to 50 psi while periodically opening V9 to verify.<br><br>"
                "Turn V8 horizontal.<br>"
                "Open V9<br><br>"
                "<i>Verify pressure is less than 30 on PG2.</i><br><br>"
            )
            self.tankpressurebeginbutton.setText("Continue")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)

        if self.tankpressure_passed[2] or self.tankpressure_failed[2] or self.current_tankpressure_step > 2:
            self.tankpressurelabel.setText(
                    "Test Complete.<br><br>"
                    "Tank Pressure Test has been completed successfully!<br>"
                )
            self.tankpressurebeginbutton.setText("Results")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressureResults)



            self.tankpressurerestart = QPushButton("Restart", self)
            self.tankpressurerestart.clicked.connect(self.TankPressureRestart)
            self.tankpressurerestart.setFixedWidth(200)
            self.tankpressuretestbuttonlayout.addWidget(self.tankpressurerestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.tankpressurenext = QPushButton("Next", self)
            self.tankpressurenext.clicked.connect(self.TankPressureNext)
            self.tankpressurenext.setFixedWidth(200)
            self.tankpressuretestbuttonlayout.addWidget(self.tankpressurenext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def TankPressureNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)

    def show_timer_popup(self):
        try:
            self.timer_window = TimerPopup(self)
            self.timer_window.show()
        except Exception as e:
            print(f"Error showing timer popup (button): {e}")

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

    def TankPressureResults(self):
        print("Printing TankPressure Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/tankpressure"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "TankPressure has not been run yet.")
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
            "step1_tankpressure_leak": "Tank Leak Inspection Test:",
            "step2_tankpressure_ventvalve": "Vent Valve Operation Test:",
            "step3_tankpressure_pressure": "Tank Pressure Verification (PSI):",
        }

        ordered_keys = [
            "step1_tankpressure_leak",
            "step2_tankpressure_ventvalve",
            "step3_tankpressure_pressure",
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
        report_lines.append("Tank Pressure Test")

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
        text = "<h2>Tank Pressure Results</h2>"
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
        win.setWindowTitle("Tank Pressure Results")
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

        self._tankpressure_results_window = win

    def TankPressureTestPath(self, path):
        self.test_path = path

    def insert_tankpressure_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Tank Pressure Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Tank Pressure section not found.")
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
            print(f"Error updating tank pressure result: {e}")

    def TankPressureRestart(self):
        try:
            print("Restarting TankPressure Test")

            # ---------- State reset ----------
            self.tankpressure_results = ""
            self.tankpressure_passed = [False] * len(self.tankpressure_passed)
            self.tankpressure_failed = [False] * len(self.tankpressure_failed)
            self.tankpressure_completed = False
            self.current_tankpressure_step = 0
            self.step_status = {}

            # ---------- Restore instructions ----------
            self.tankpressurelabel.setText(
                "<b>Remove plastic drain tube from clip behind server.<br><br>"
            "Use 11/16 wrench to remove pressure relief valve.<br><br>"
            "Use a 7/16 wrench to secure 1/8 inch NPT plug wrapped with teflon tape.<br><br>"
            "1. Replace the pressure relief valve with a 1/8 inch NPT plug prior to " 
            "testing.<br><br>"
            "Close V10 then turn V8 vertical. <br><br>"
            "2. Connect the Beverage Maker to water supply and then open V10.<br><br>"
            "3. Let tank fill with water. Flow meter will go to zero when tank is full.<br><br>" 
            "4. Adjust water pressure by rotating V7 clockwise until PG2 reads 130 psig (8.96 barg).<br><br>"
            "Hold for a minimum of 5 minutes.<br><br>"
            "Inspect tank for leaks.<br><br>"
            "<i>No leaks are allowed.</i><br><br>"
            )

            # ---------- Remove completion buttons ----------
            if hasattr(self, "tankpressurerestart") and self.tankpressurerestart:
                self.tankpressuretestbuttonlayout.removeWidget(self.tankpressurerestart)
                self.tankpressurerestart.deleteLater()
                self.tankpressurerestart = None

            if hasattr(self, "tankpressurenext") and self.tankpressurenext:
                self.tankpressuretestbuttonlayout.removeWidget(self.tankpressurenext)
                self.tankpressurenext.deleteLater()
                self.tankpressurenext = None

            # ---------- Restore Begin button ----------
            self.tankpressurebeginbutton.setText("Begin")
            try:
                self.tankpressurebeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)

        except Exception as e:
            print(f"Error restarting TankPressure Test: {e}")


    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[TankPressure] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

    def PostTankPressureResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Tank Pressure: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/tankpressure"
            r = requests.post(url, json=payload, timeout=5)
            print("Tank Pressure POST status:", r.status_code)
            print("Tank Pressure POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Tank Pressure result: {e}")

    def post_tankpressure_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.tankpressure_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.tankpressure_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.tankpressure_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostTankPressureResults(status=overall_status, data=data, notes=notes)

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
        html = resource_path(
            "Unity",
            "WebGL",
            "index.html"
        )

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

            pdf_path = resource_path(
                "Resources",
                f"{cmm}.pdf"
            )

            if platform.system() == "Darwin":
                subprocess.run(["open", str(pdf_path)])
            elif platform.system() == "Windows":
                os.startfile(str(pdf_path))
            else:
                subprocess.run(["xdg-open", str(pdf_path)])

        except Exception as e:
            print(f"Error loading CMM: {e}")

    def LoadModel(self):
        try:
            self.start_webgl()
        except Exception as e:
            print(f"Error loading 3D Model: {e}")

    def SubtestsCompleted(self):
        if self.test_id is None or self.api_base_url is None:
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/tankpressure"
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
                self.current_tankpressure_step = 3
                print(f"Current step: {self.current_tankpressure_step}")
                self.updateTankPressureStep()

            elif status == "INCOMPLETE":
                steps = payload.get("data", {}).get("steps", {})
                # Resume at "next" step index
                self.current_tankpressure_step = len(steps)
                print(f"Current step: {self.current_tankpressure_step}")
                self.updateTankPressureStep()
                return

            self.updateTankPressureStep()

        except Exception as e:
            print(f"[TankPressure] sync_completed_from_db failed: {e}")

class TimerPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setWindowTitle("Timer")
            self.setFixedSize(300, 200)

            self.seconds = 0
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_time)

            # ---- Layout ----
            layout = QVBoxLayout(self)

            self.time_label = QLabel("00:00:00")
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.time_label.setStyleSheet("font-size: 32px; font-weight: bold;")
            layout.addWidget(self.time_label)

            button_layout = QHBoxLayout()

            self.start_button = QPushButton("Start")
            self.stop_button = QPushButton("Stop")
            self.restart_button = QPushButton("Restart")

            self.start_button.clicked.connect(self.start_timer)
            self.stop_button.clicked.connect(self.stop_timer)
            self.restart_button.clicked.connect(self.restart_timer)

            button_layout.addWidget(self.start_button)
            button_layout.addWidget(self.stop_button)
            button_layout.addWidget(self.restart_button)

            layout.addLayout(button_layout)
        except Exception as e:
            print(f"Error while creating Timer: {e}")

    def update_time(self):
        self.seconds += 1
        hrs = self.seconds // 3600
        mins = (self.seconds % 3600) // 60
        secs = self.seconds % 60
        self.time_label.setText(f"{hrs:02}:{mins:02}:{secs:02}")

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(1000)

    def stop_timer(self):
        self.timer.stop()

    def restart_timer(self):
        self.timer.stop()
        self.seconds = 0
        self.time_label.setText("00:00:00")