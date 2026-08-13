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

from Python.Automation.BDaq.InstantDoCtrl import InstantDoCtrl


class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- HeaterCurrent Check

class HeaterCurrentTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.heatercurrent_results = ""
        self.heatercurrent_passed = [False, False, False, False]
        self.heatercurrent_failed = [False, False, False, False]
        self.heatercurrent_completed = False
        self.current_heatercurrent_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phaseAread = 0
        self.phaseBread = 0
        self.phaseCread = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.heatercurrentlabellayout = QHBoxLayout()
        self.heatercurrenttestbuttonlayout = QHBoxLayout()

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
                        min_value-height: 20px;
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
                        min_value-width: 20px;
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

        self.heatercurrentlabel = QLabel(
            "<b>Press ON/OFF switch (this activates the electric vent valve).</b> <br><br>"
            "<i>   FM should read above 0 as the water tank completes filling. </i><br><br>"
        )

        self.heatercurrentlabel.setTextFormat(Qt.TextFormat.RichText)
        self.heatercurrentlabel.setWordWrap(True)
        self.heatercurrentlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.heatercurrentlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.heatercurrentlabel)


        self.heatercurrentlabellayout.addWidget(scroll)
        layout.addLayout(self.heatercurrentlabellayout)
        layout.addLayout(self.heatercurrenttestbuttonlayout)
        try:
            self.heatercurrentbeginbutton = QPushButton("Begin")
            self.heatercurrentbeginbutton.setFixedWidth(200)
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrent)
            self.heatercurrenttestbuttonlayout.addWidget(self.heatercurrentbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def HeaterCurrent(self):
        try:
            msg1 = QMessageBox()

            if self.current_heatercurrent_step == 0:
                msg1.setWindowTitle("Check Flow Meter")
                msg1.setText("Flow Meter reads above 0 after filling has completed.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Flow Meter Test: "
                    result_line += "\tPASS"
                    self.insert_heatercurrent_result(result_line)
                    self.step_status["step1_heatercurrent_flow"] = {
                        "status": "PASS"
                    }
                    self.post_heatercurrent_snapshot()
                    self.heatercurrent_passed[0] = True
                    self.heatercurrent_failed[0] = False
                    self.heatercurrent_completed = True
                    self.updateHeaterCurrentStep()
                    self.current_heatercurrent_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Flow Meter Test: "
                    result_line += "\tFAIL"
                    self.insert_heatercurrent_result(result_line)
                    self.step_status["step1_heatercurrent_flow"] = {
                        "status": "FAIL"
                    }
                    self.post_heatercurrent_snapshot()
                    self.heatercurrent_passed[0] = False
                    self.heatercurrent_failed[0] = True
                    self.updateHeaterCurrentStep()
                    self.current_heatercurrent_step += 1

                    # STEP 1 — 4.5 mΩ
            elif self.current_heatercurrent_step == 1:
                msg1.setWindowTitle("Check LOW Indicator Light")
                msg1.setText("The LOW Indicator Light is activated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"LOW Indicator Light Test: "
                    result_line += "\tPASS"
                    self.insert_heatercurrent_result(result_line)
                    self.step_status["step2_heatercurrent_lowindicator"] = {
                        "status": "PASS"
                    }
                    self.post_heatercurrent_snapshot()
                    self.heatercurrent_passed[1] = True
                    self.heatercurrent_failed[1] = False
                    self.heatercurrent_completed = True
                    self.updateHeaterCurrentStep()
                    self.current_heatercurrent_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"LOW Indicator Light Test: "
                    result_line += "\tFAIL"
                    self.insert_heatercurrent_result(result_line)
                    self.step_status["step2_heatercurrent_lowindicator"] = {
                        "status": "FAIL"
                    }
                    self.post_heatercurrent_snapshot()
                    self.heatercurrent_passed[1] = False
                    self.heatercurrent_failed[1] = True
                    self.updateHeaterCurrentStep()
                    self.current_heatercurrent_step += 1

                msg1 = QMessageBox()
                # msg1.setIcon(QMessageBox.Icon.Information)

                if self.current_heatercurrent_step == 2:
                    value1, ok = NumericKeypadDialog.getValue(
                        self,
                        "Phase A",
                        "Please enter the current of Phase A as displayed by the self.phase readings window.",
                        decimals=2,
                        min_value=0.0,
                       max_value=50.0,
                    )
                    self.heatercurrent_results += f"Phase A: {value1} A\n"
                    if ok:
                        result_line = f"Phase A: {value1} A"
                        if value1 >= 7 and value1 <= 9:   #----------------------------------------- Check these limits.
                            result_line += "\tPASS"
                            self.step_status["step3_heatercurrent_phasea"] = {
                                "status": "PASS",
                                "value": value1
                            }
                            self.post_heatercurrent_snapshot()
                            self.heatercurrent_passed[1] = True
                            self.heatercurrent_failed[1] = False
                        else:
                            result_line += "\tFAIL"
                            self.step_status["step3_heatercurrent_phasea"] = {
                                "status": "FAIL",
                                "value": value1
                            }
                            self.post_heatercurrent_snapshot()
                            self.heatercurrent_passed[1] = False
                            self.heatercurrent_failed[1] = True
                        self.insert_heatercurrent_result(result_line)

                        self.current_heatercurrent_step += 1

                        if self.current_heatercurrent_step == 3:
                            value1, ok = NumericKeypadDialog.getValue(
                                self,
                                "Phase B",
                                "Please enter the current of Phase B as displayed by the self.phase readings window.",
                                decimals=2,
                                min_value=0.0,
                               max_value=50.0,
                            )
                            self.heatercurrent_results += f"Phase B: {value1} A\n"
                            if ok:
                                result_line = f"Phase B: {value1} A"
                                if value1 >= 7 and value1 <= 9:  # ----------------------------------------- Check these limits.
                                    result_line += "\tPASS"
                                    self.step_status["step4_heatercurrent_phaseb"] = {
                                        "status": "PASS",
                                        "value": value1
                                    }
                                    self.post_heatercurrent_snapshot()
                                    self.heatercurrent_passed[2] = True
                                    self.heatercurrent_failed[2] = False
                                else:
                                    result_line += "\tFAIL"
                                    self.step_status["step4_heatercurrent_phaseb"] = {
                                        "status": "FAIL",
                                        "value": value1
                                    }
                                    self.post_heatercurrent_snapshot()
                                    self.heatercurrent_passed[2] = False
                                    self.heatercurrent_failed[2] = True
                                self.insert_heatercurrent_result(result_line)
                                self.current_heatercurrent_step += 1



                                if self.current_heatercurrent_step == 4:
                                    print(self.current_heatercurrent_step)
                                    value1, ok = NumericKeypadDialog.getValue(
                                        self,
                                        "Phase C",
                                        "Please enter the current of Phase C as displayed by the self.phase readings window.",
                                        decimals=2,
                                        min_value=0.0,
                                        max_value=50.0,

                                    )
                                    self.heatercurrent_results += f"Phase C: {value1} A\n"
                                    if ok:
                                        result_line = f"Phase C: {value1} A"
                                        if value1 >= 7 and value1 <= 9:  # ----------------------------------------- Check these limits.
                                            result_line += "\tPASS"
                                            self.step_status["step5_heatercurrent_phasec"] = {
                                                "status": "PASS",
                                                "value": value1
                                            }
                                            self.post_heatercurrent_snapshot()
                                            self.heatercurrent_passed[3] = True
                                            self.heatercurrent_failed[3] = False
                                        else:
                                            result_line += "\tFAIL"
                                            self.step_status["step5_heatercurrent_phasec"] = {
                                                "status": "FAIL",
                                                "value": value1
                                            }
                                            self.post_heatercurrent_snapshot()
                                            self.heatercurrent_passed[3] = False
                                            self.heatercurrent_failed[3] = True
                                        self.insert_heatercurrent_result(result_line)
                                        self.heatercurrent_completed = True
                                        self.updateHeaterCurrentStep()
                                        self.current_heatercurrent_step += 1
                                        self.post_heatercurrent_snapshot()




            # Completed
            elif self.heatercurrent_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The HeaterCurrent test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateHeaterCurrentStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHeaterCurrentStep(self):

        # ----------------------------
        # Completion screen MUST win
        # ----------------------------
        if (self.heatercurrent_passed[2] or self.heatercurrent_failed[2] or
                self.current_heatercurrent_step > 4):

            self.heatercurrentlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Heater Current test has been completed successfully!</b><br><br>"
            )

            self.heatercurrentbeginbutton.setText("Results")
            try:
                self.heatercurrentbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrentResults)

            # Don't stack duplicate buttons if updateHeaterCurrentStep runs again
            if not (hasattr(self, "heatercurrentrestart") and self.heatercurrentrestart):
                self.heatercurrentrestart = QPushButton("Restart", self)
                self.heatercurrentrestart.clicked.connect(self.HeaterCurrentRestart)
                self.heatercurrentrestart.setFixedWidth(200)
                self.heatercurrenttestbuttonlayout.addWidget(
                    self.heatercurrentrestart,
                    alignment=Qt.AlignmentFlag.AlignCenter
                )

            if not (hasattr(self, "heatercurrentnext") and self.heatercurrentnext):
                self.heatercurrentnext = QPushButton("Next", self)
                self.heatercurrentnext.clicked.connect(self.HeaterCurrentNext)
                self.heatercurrentnext.setFixedWidth(200)
                self.heatercurrenttestbuttonlayout.addWidget(
                    self.heatercurrentnext,
                    alignment=Qt.AlignmentFlag.AlignCenter
                )

            return  # critical: prevent step screens below from overwriting completion UI

        # ----------------------------
        # Step screens (kept EXACTLY)
        # ----------------------------
        if self.heatercurrent_passed[0] or self.heatercurrent_failed[0]:
            print("Update Heater Current Step")
            self.heatercurrentlabel.setText(
                "  <i> The LOW WATER lamp should turn off once tank is full. </i><br><br>"
            )
            self.heatercurrentbeginbutton.setText("Continue")
            try:
                self.heatercurrentbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrent)

        if self.heatercurrent_passed[1] or self.heatercurrent_failed[1]:
            print("Update Heater Current Step")
            self.heatercurrentlabel.setText(
                " <b>  Each heater should draw approximately 8±1 amps</b> <br><br>"
                " <i>  Please enter the amperage of Phase A as displayed by the self.phase readings window </i><br><br>"
            )
            self.heatercurrentbeginbutton.setText("Continue")
            try:
                self.heatercurrentbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrent)

    def HeaterCurrentNext(self):
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

    def HeaterCurrentResults(self):
        print("Printing HeaterCurrent Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/heatercurrent"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "HeaterCurrent has not been run yet.")
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
            "step1_heatercurrent_flow": "Flow Meter Verification Test:",
            "step2_heatercurrent_lowindicator": "LOW Indicator Light Test:",
            "step3_heatercurrent_phasea": "Phase A Heater Current (A):",
            "step4_heatercurrent_phaseb": "Phase B Heater Current (A):",
            "step5_heatercurrent_phasec": "Phase C Heater Current (A):",
        }

        ordered_keys = [
            "step1_heatercurrent_flow",
            "step2_heatercurrent_lowindicator",
            "step3_heatercurrent_phasea",
            "step4_heatercurrent_phaseb",
            "step5_heatercurrent_phasec",
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
        report_lines.append("Heater Current Test")

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
        text = "<h2>Heater Current Results</h2>"
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
        win.setWindowTitle("Heater Current Results")
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

        self._heatercurrent_results_window = win

    def HeaterCurrentTestPath(self, path):
        self.test_path = path

    def insert_heatercurrent_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Heater Current Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Heater Current section not found.")
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

    def HeaterCurrentRestart(self):
        try:
            print("Restarting HeaterCurrent Test")

            # ---------- State reset ----------
            self.heatercurrent_results = ""
            self.heatercurrent_passed = [False] * len(self.heatercurrent_passed)
            self.heatercurrent_failed = [False] * len(self.heatercurrent_failed)
            self.heatercurrent_completed = False
            self.current_heatercurrent_step = 0
            self.step_status = {}

            # ---------- Restore instructions ----------
            self.heatercurrentlabel.setText(
                "<b>Press ON/OFF switch (this activates the electric vent valve).</b> <br><br>"
            "<i>   FM should read above 0 as the water tank completes filling. </i><br><br>"
            )

            # ---------- Remove completion buttons ----------
            if hasattr(self, "heatercurrentrestart") and self.heatercurrentrestart:
                self.heatercurrenttestbuttonlayout.removeWidget(self.heatercurrentrestart)
                self.heatercurrentrestart.deleteLater()
                self.heatercurrentrestart = None

            if hasattr(self, "heatercurrentnext") and self.heatercurrentnext:
                self.heatercurrenttestbuttonlayout.removeWidget(self.heatercurrentnext)
                self.heatercurrentnext.deleteLater()
                self.heatercurrentnext = None

            # ---------- Restore Begin button ----------
            self.heatercurrentbeginbutton.setText("Begin")
            try:
                self.heatercurrentbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrent)

        except Exception as e:
            print(f"Error restarting HeaterCurrent Test: {e}")


    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[HeaterCurrent] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

    def PostHeaterCurrentResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Heater Current: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/heatercurrent"
            r = requests.post(url, json=payload, timeout=5)
            print("Heater Current POST status:", r.status_code)
            print("Heater Current POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Heater Current result: {e}")

    def post_heatercurrent_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.heatercurrent_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.heatercurrent_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.heatercurrent_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostHeaterCurrentResults(status=overall_status, data=data, notes=notes)


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
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/heatercurrent"
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
                self.current_heatercurrent_step = 5
                print(f"Current step: {self.current_heatercurrent_step}")
                self.updateHeaterCurrentStep()

            elif status == "INCOMPLETE":
                steps = payload.get("data", {}).get("steps", {})
                # Resume at "next" step index
                self.current_heatercurrent_step = len(steps)
                print(f"Current step: {self.current_heatercurrent_step}")
                self.updateHeaterCurrentStep()
                return

            self.updateHeaterCurrentStep()

        except Exception as e:
            print(f"[HeaterCurrent] sync_completed_from_db failed: {e}")

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