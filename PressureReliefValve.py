from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog, QComboBox, QDialog
)

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QUrl, QTimer

from InstrumentWorker import InstrumentWorker

from NumPad import NumericKeypadDialog

import requests
import subprocess
import platform
import os
import sys

from pathlib import Path
from paths import resource_path

from Python.Automation.BDaq.InstantDoCtrl import InstantDoCtrl


class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- PressureReliefValve Check

class PressureReliefValveTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.pressurereliefvalve_results = ""
        self.pressurereliefvalve_passed = [False, False, False]
        self.pressurereliefvalve_failed = [False, False, False]
        self.pressurereliefvalve_completed = False
        self.current_pressurereliefvalve_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phaseAread = 0
        self.phaseBread = 0
        self.phaseCread = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.pressurereliefvalvelabellayout = QHBoxLayout()
        self.pressurereliefvalvetestbuttonlayout = QHBoxLayout()

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

        self.pressurereliefvalvelabel = QLabel(
            "<b>Remove brew cup assembly. <br><br>"
            "Close V10 then turn V8 vertical. <br><br>"
            "Connect the Coffee Maker to water supply and then open V10. <br><br>"
            "Let tank fill with water, FM will go to zero when full. <br><br>"
            "With water tank full, increase source water pressure by rotating V7 clockwise while venting V9 periodically until pressure relief valve opens.<br><br>"
            "Verify the pressure relief valve opens as indicated by water dripping in brew cup assembly housing. </b><br><br>"
            "<i>Make sure that the pressure relief valve opens at 95±10 PSIG.</i> <br><br>"

        )

        self.pressurereliefvalvelabel.setTextFormat(Qt.TextFormat.RichText)
        self.pressurereliefvalvelabel.setWordWrap(True)
        self.pressurereliefvalvelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.pressurereliefvalvelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.pressurereliefvalvelabel)


        self.pressurereliefvalvelabellayout.addWidget(scroll)
        layout.addLayout(self.pressurereliefvalvelabellayout)
        layout.addLayout(self.pressurereliefvalvetestbuttonlayout)
        try:
            self.pressurereliefvalvebeginbutton = QPushButton("Begin")
            self.pressurereliefvalvebeginbutton.setFixedWidth(200)
            self.pressurereliefvalvebeginbutton.clicked.connect(self.PressureReliefValve)
            self.pressurereliefvalvetestbuttonlayout.addWidget(self.pressurereliefvalvebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def PressureReliefValve(self):
        try:
            do = InstantDoCtrl("PCIE-1761H,BID#0")
            ret1 = do.writeAny(0, 1, [0x60])
            print(ret1)
            msg1 = QMessageBox()

            if self.current_pressurereliefvalve_step == 0:
                value1, ok = NumericKeypadDialog.getValue(
                    self,
                    "Pressure Relief Valve",
                    "Please enter the pressure with which the Pressure Relief Valve opens",
                    decimals=2,
                    min_value=0.0,
                    max_value=200.0,
                )
                self.pressurereliefvalve_results += f""
                if ok:
                    result_line = f"Pressure Relief Valve Operational Pressure: {value1} PSIG \n"
                    if value1 >= 85 and value1 <= 105:
                        result_line += "\tPASS"
                        self.step_status["step1_pressurereliefvalve_open"] = {
                            "status": "PASS",
                            "value": value1
                        }
                        self.post_pressurereliefvalve_snapshot()
                        self.current_pressurereliefvalve_step += 1
                        self.pressurereliefvalve_passed[0] = True
                        self.pressurereliefvalve_failed[0] = False
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step1_pressurereliefvalve_open"] = {
                            "status": "FAIL",
                            "value": value1
                        }
                        self.post_pressurereliefvalve_snapshot()
                        self.current_pressurereliefvalve_step += 1
                        self.pressurereliefvalve_passed[0] = False
                        self.pressurereliefvalve_failed[0] = True

                    self.insert_pressurereliefvalve_result(result_line)
                    self.updatePressureReliefValveStep()

            elif self.current_pressurereliefvalve_step == 1:
                msg1.setWindowTitle("Pressure Relief Valve Leak Check")
                msg1.setText("No pressure relief valve leaks observed.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Pressure Relief Valve Leak Check: "
                    result_line += "\tPASS"
                    self.step_status["step1_pressurereliefvalve_leak"] = {
                        "status": "PASS",
                    }
                    self.post_pressurereliefvalve_snapshot()
                    self.insert_pressurereliefvalve_result(result_line)
                    self.pressurereliefvalve_passed[1] = True
                    self.pressurereliefvalve_failed[1] = False
                    self.current_pressurereliefvalve_step += 1
                    self.updatePressureReliefValveStep()


                elif msg1.clickedButton() == fail_button:
                    result_line = f"Pressure Relief Valve Leak Check: "
                    result_line += "\tFAIL"
                    self.step_status["step1_pressurereliefvalve_leak"] = {
                        "status": "FAIL",
                    }
                    self.post_pressurereliefvalve_snapshot()
                    self.insert_pressurereliefvalve_result(result_line)
                    self.pressurereliefvalve_passed[1] = False
                    self.pressurereliefvalve_failed[1] = True
                    self.updatePressureReliefValveStep()


            elif self.current_pressurereliefvalve_step == 2:
                value1, ok = NumericKeypadDialog.getValue(
                    self,
                    "Vented Relief Pressure",
                    "Please enter the pressure observed on PG2 after venting",
                    decimals=2,
                    min_value=0.0,
                    max_value=100.0,
                )
                self.pressurereliefvalve_results += f""
                if ok:
                    result_line = f"Vented Pressure: {value1} PSIG \n"
                    if value1 <= 30:
                        result_line += "\tPASS"
                        self.step_status["step3_pressurereliefvalve_vent"] = {
                            "status": "PASS",
                            "value": value1
                        }
                        self.post_pressurereliefvalve_snapshot()
                        self.pressurereliefvalve_passed[2] = True
                        self.pressurereliefvalve_failed[2] = False
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step3_pressurereliefvalve_vent"] = {
                            "status": "FAIL",
                            "value": value1
                        }
                        self.post_pressurereliefvalve_snapshot()
                        self.pressurereliefvalve_passed[2] = False
                        self.pressurereliefvalve_failed[2] = True

                    self.insert_pressurereliefvalve_result(result_line)
                    self.current_pressurereliefvalve_step += 1
                    self.pressurereliefvalve_completed = True
                    self.updatePressureReliefValveStep()
                    self.post_pressurereliefvalve_snapshot()

            # Completed
            elif self.pressurereliefvalve_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Pressure Relief Valve test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updatePressureReliefValveStep()

        except Exception as e:
            print(f"Error: {e}")

    def updatePressureReliefValveStep(self):

        if self.current_pressurereliefvalve_step == 1:
            print("Update Pressure Relief Valve Step")
            self.pressurereliefvalvelabel.setText(
                "Check for leaks after 5 minutes. <br><br>"
                "<i>No leaks are to be observed </i><br><br>"
            )
            self.pressurereliefvalvebeginbutton.setText("Continue")
            self.pressurereliefvalvebeginbutton.clicked.disconnect()
            self.pressurereliefvalvebeginbutton.clicked.connect(self.PressureReliefValve)

        if self.current_pressurereliefvalve_step == 2:
            print("Update Pressure Relief Valve Step")
            self.pressurereliefvalvelabel.setText(
                "<b>Disconnect water by turning off V10. <br><br>"
                "Drain the coffee maker tank by opening V11. <br><br>"
                "Slowly rotate V7 counterclockwise until PG2 reads below 50 psig.</b><br><br>"
                "<i>Turn V8 horizontal and vent V9 to verify PG2 reads below 30 psig.</i> <br><br>"
                "Close V11 once confirmed."
            )
            self.pressurereliefvalvebeginbutton.setText("Continue")
            self.pressurereliefvalvebeginbutton.clicked.disconnect()
            self.pressurereliefvalvebeginbutton.clicked.connect(self.PressureReliefValve)


        if self.pressurereliefvalve_completed == True or self.current_pressurereliefvalve_step > 2:
            self.pressurereliefvalvelabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Pressure Relief Valve test has been completed successfully!</b><br><br>"
            )
            self.pressurereliefvalvebeginbutton.setText("Results")
            self.pressurereliefvalvebeginbutton.clicked.disconnect()
            self.pressurereliefvalvebeginbutton.clicked.connect(self.PressureReliefValveResults)

            self.pressurereliefvalverestart = QPushButton("Restart", self)
            self.pressurereliefvalverestart.clicked.connect(self.PressureReliefValveRestart)
            self.pressurereliefvalverestart.setFixedWidth(200)
            self.pressurereliefvalvetestbuttonlayout.addWidget(self.pressurereliefvalverestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.pressurereliefvalvenext = QPushButton("Next", self)
            self.pressurereliefvalvenext.clicked.connect(self.PressureReliefValveNext)
            self.pressurereliefvalvenext.setFixedWidth(200)
            self.pressurereliefvalvetestbuttonlayout.addWidget(self.pressurereliefvalvenext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def PressureReliefValveNext(self):
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

    def PressureReliefValveResults(self):
        print("Printing PressureReliefValve Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/pressurereliefvalve"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "PressureReliefValve has not been run yet.")
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
            "step1_pressurereliefvalve_open": "Pressure Relief Valve Opening Pressure (PSIG):",
            "step1_pressurereliefvalve_leak": "Pressure Relief Valve Leak Check:",
            "step3_pressurereliefvalve_vent": "Vented Relief Pressure After Drain (PSIG):",
        }

        ordered_keys = [
            "step1_pressurereliefvalve_open",
            "step1_pressurereliefvalve_leak",
            "step3_pressurereliefvalve_vent",
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
        report_lines.append("Pressure and Relief Valve Test")

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
        text = "<h2>Pressure Relief Valve Results</h2>"
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
        win.setWindowTitle("Pressure Relief Valve Results")
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

        self._pressurereliefvalve_results_window = win

    def PressureReliefValveTestPath(self, path):
        self.test_path = path

    def insert_pressurereliefvalve_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Pressure Relief Valve Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Pressure Relief Valve section not found.")
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

    def PressureReliefValveRestart(self):
        try:
            print("Restarting PressureReliefValve Test")

            # ---------- State reset ----------
            self.pressurereliefvalve_results = ""
            self.pressurereliefvalve_passed = [False] * len(self.pressurereliefvalve_passed)
            self.pressurereliefvalve_failed = [False] * len(self.pressurereliefvalve_failed)
            self.pressurereliefvalve_completed = False
            self.current_pressurereliefvalve_step = 0
            self.step_status = {}

            # ---------- Restore instructions ----------
            self.pressurereliefvalvelabel.setText(
                "<b>Remove brew cup assembly. <br><br>"
            "Close V10 then turn V8 vertical. <br><br>"
            "Connect the Coffee Maker to water supply and then open V10. <br><br>"
            "Let tank fill with water, FM will go to zero when full. <br><br>"
            "With water tank full, increase source water pressure by rotating V7 clockwise while venting V9 periodically until pressure relief valve opens.<br><br>"
            "Verify the pressure relief valve opens as indicated by water dripping in brew cup assembly housing. </b><br><br>"
            "<i>Make sure that the pressure relief valve opens at 95±10 PSIG.</i> <br><br>"
            )

            # ---------- Remove completion buttons ----------
            if hasattr(self, "pressurereliefvalverestart") and self.pressurereliefvalverestart:
                self.pressurereliefvalvetestbuttonlayout.removeWidget(self.pressurereliefvalverestart)
                self.pressurereliefvalverestart.deleteLater()
                self.pressurereliefvalverestart = None

            if hasattr(self, "pressurereliefvalvenext") and self.pressurereliefvalvenext:
                self.pressurereliefvalvetestbuttonlayout.removeWidget(self.pressurereliefvalvenext)
                self.pressurereliefvalvenext.deleteLater()
                self.pressurereliefvalvenext = None

            # ---------- Restore Begin button ----------
            self.pressurereliefvalvebeginbutton.setText("Begin")
            try:
                self.pressurereliefvalvebeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.pressurereliefvalvebeginbutton.clicked.connect(self.PressureReliefValve)

        except Exception as e:
            print(f"Error restarting PressureReliefValve Test: {e}")


    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[PressureReliefValve] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

    def PostPressureReliefValveResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Pressure Relief Valve: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/pressurereliefvalve"
            r = requests.post(url, json=payload, timeout=5)
            print("Pressure Relief Valve POST status:", r.status_code)
            print("Pressure Relief Valve POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Pressure Relief Valve result: {e}")

    def post_pressurereliefvalve_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.pressurereliefvalve_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.pressurereliefvalve_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.pressurereliefvalve_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostPressureReliefValveResults(status=overall_status, data=data, notes=notes)


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
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/pressurereliefvalve"
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
                self.current_pressurereliefvalve_step = 2
                print(f"Current step: {self.current_pressurereliefvalve_step}")
                self.updatePressureReliefValveStep()

            elif status == "INCOMPLETE":
                steps = payload.get("data", {}).get("steps", {})
                # Resume at "next" step index
                self.current_pressurereliefvalve_step = len(steps)
                print(f"Current step: {self.current_pressurereliefvalve_step}")
                self.updatePressureReliefValveStep()
                return

            self.updatePressureReliefValveStep()

        except Exception as e:
            print(f"[PressureRelief] sync_completed_from_db failed: {e}")

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
