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



#------------------------------------------------------- RTDCircuit Check

class RTDCircuitTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()

        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        self.rtdcircuit_results = ""
        self.rtdcircuit_passed = [False, False, False, False]
        self.rtdcircuit_failed = [False, False, False, False]
        self.rtdcircuit_completed = False
        self.current_rtdcircuit_step = 0

        self.step_status = {}

        # -------- temp self.phase
        self.phaseAread = 0
        self.phaseBread = 0
        self.phaseCread = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.rtdcircuitlabellayout = QHBoxLayout()
        self.rtdcircuittestbuttonlayout = QHBoxLayout()

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

        self.rtdcircuitlabel = QLabel(
            "<b>1. With the Beverage Maker connected to the water supply and the red lever on the EDB in the OFF position,"
            " remove the cover from the power module assy and disconnect the RTD assy plug (P4) from the J4"
            " connector on the controller board assy.<br><br>"
            "2. Connect the DMM (set to ohms scale) to the RTD simulator harness (IAS11003A).<br><br>"
            "Rotate the knob until 1430±1 ohms is indicated on the DMM.<br><br>"
            "Change DMM to DC volts then connect harness inline between the controller board assy (J4) and P4.<br><br>"
            "3. Connect the Beverage Maker to the power supply.<br><br>"
            "Set the red lever on the EDB to the ON position.<br><br>"
            "4. Press the power button.<br><br>"
            "<i>This should trip the safety latch.</i><br><br>"
            "<i>(If the safety latch is tripped, there will be no current drawn to the heaters and the power indicator light should go into double-blink mode.)</i><br><br>"
            )

        self.rtdcircuitlabel.setTextFormat(Qt.TextFormat.RichText)
        self.rtdcircuitlabel.setWordWrap(True)
        self.rtdcircuitlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.rtdcircuitlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.rtdcircuitlabel)

        self.rtdcircuitlabellayout.addWidget(scroll)
        layout.addLayout(self.rtdcircuitlabellayout)
        layout.addLayout(self.rtdcircuittestbuttonlayout)
        try:
            self.rtdcircuitbeginbutton = QPushButton("Begin")
            self.rtdcircuitbeginbutton.setFixedWidth(200)
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        except Exception as e:
            print(f"Error while opening workorder: {e}")

        # -------------------------------------------------------------------- Phase Readings

        self.bottomToolbar = QHBoxLayout()

        self.phaselayout = QVBoxLayout()

        self.resources = QPushButton("Resources")
        self.resources.setFixedWidth(200)
        self.resources.clicked.connect(self.OnResources)
        self.bottomToolbar.addWidget(self.resources)

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

    def RTDCircuit(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_rtdcircuit_step == 0:
                msg1.setWindowTitle("Safety Latch Check")
                msg1.setText("Safety Latch engaged and unit entered double-blink mode.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Test: "
                    result_line += "\tPASS"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step1_rtdcircuit_doubleblink"] = {
                        "status": "PASS",
                    }
                    self.post_rtdcircuit_snapshot()
                    self.rtdcircuit_passed[0] = True
                    self.rtdcircuit_failed[0] = False
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Test: "
                    result_line += "\tFAIL"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step1_rtdcircuit_doubleblink"] = {
                        "status": "FAIL",
                    }
                    self.post_rtdcircuit_snapshot()
                    self.rtdcircuit_passed[0] = False
                    self.rtdcircuit_failed[0] = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_rtdcircuit_step == 1:
                msg1.setWindowTitle("Safety Latch Reset Check")
                msg1.setText("Safety Latch did not engage after resetting and unit did not enter double-blink mode.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Reset Test: "
                    result_line += "\tPASS"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step2_rtdcircuit_safetylatch"] = {
                        "status": "PASS",
                    }

                    self.rtdcircuit_passed[1] = True
                    self.rtdcircuit_failed[1] = False
                    self.post_rtdcircuit_snapshot()
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Safety Latch Trip and Double Blink Mode Reset Test: "
                    result_line += "\tFAIL"
                    self.insert_rtdcircuit_result(result_line)
                    self.step_status["step2_rtdcircuit_safetylatch"] = {
                        "status": "FAIL",
                    }

                    self.rtdcircuit_passed[1] = False
                    self.rtdcircuit_failed[1] = True
                    self.post_rtdcircuit_snapshot()
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_rtdcircuit_step == 2:
                value, ok = NumericKeypadDialog.getValue(
                    self,
                    "Voltage Check",
                    "Please enter the voltage measurement observed on DMM:",
                    decimals=3,
                    min_value=0.0,
                    max_value=100.0,
                )

                self.rtdcircuit_results += f"Voltage Result: {value} volts\n"
                if ok:
                    result_line = f"Voltage Result: {value} volts"
                    if value <= 2.06:
                        result_line += "\tPASS"
                        self.step_status["step3_rtdcircuit_voltage"] = {
                            "status": "PASS",
                            "value": value
                        }
                        self.post_rtdcircuit_snapshot()
                    else:
                        result_line += "\tFAIL"
                        self.step_status["step3_rtdcircuit_voltage"] = {
                            "status": "FAIL",
                            "value": value
                        }
                        self.post_rtdcircuit_snapshot()
                    self.insert_rtdcircuit_result(result_line)
                    if value <= 2.06:
                        self.rtdcircuit_passed[2] = True
                        self.rtdcircuit_failed[2] = False

                    else:
                        self.rtdcircuit_passed[2] = False
                        self.rtdcircuit_failed[2] = True
                    self.post_rtdcircuit_snapshot()
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                return

            # STEP 4 — 5.7 mΩ
            elif self.current_rtdcircuit_step == 3:
                    msg1.setWindowTitle("Safety Latch Check")
                    msg1.setText("Safety Latch not engaged.<br><br>")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        result_line = f"Safety Latch Trip and Double Blink Mode Final Test: "
                        result_line += "\tPASS"
                        self.insert_rtdcircuit_result(result_line)
                        self.step_status["step4_rtdcircuit_safetylatchtrip"] = {
                            "status": "PASS",
                        }
                        self.post_rtdcircuit_snapshot()
                        self.rtdcircuit_passed[3] = True
                        self.rtdcircuit_failed[3] = False
                        self.rtdcircuit_completed = True
                        self.post_rtdcircuit_snapshot()
                        self.updateRTDCircuitStep()
                        self.current_rtdcircuit_step += 1
                    elif msg1.clickedButton() == fail_button:
                        result_line = f"Safety Latch Trip and Double Blink Mode Final Test: "
                        result_line += "\tPASS"
                        self.insert_rtdcircuit_result(result_line)
                        self.step_status["step4_rtdcircuit_safetylatchtrip"] = {
                            "status": "FAIL",
                        }
                        self.post_rtdcircuit_snapshot()
                        self.rtdcircuit_passed[3] = False
                        self.rtdcircuit_failed[3] = True
                        self.rtdcircuit_completed = True
                        self.post_rtdcircuit_snapshot()
                        self.updateRTDCircuitStep()
                        self.current_rtdcircuit_step += 1

            # Completed
            elif self.rtdcircuit_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The RTD Circuit test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateRTDCircuitStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateRTDCircuitStep(self):
        if self.rtdcircuit_passed[0] or self.rtdcircuit_failed[0]:
            self.rtdcircuitlabel.setText(
                "5. Rotate the knob counterclockwise until 2.365±0.003 volts is shown on the DMM.<br><br>"
                "6. Press the power button to turn the Beverage Maker off. <br><br>"
                "7. Reset the safety latch by pressing the manual switch on the back of the power module assy under the grommet.<br><br>"
                "8. Press the power button.<br>"
                "<i>While no current is being drawn by the heaters, the safety latch should not trip and the power indicator light should not go into double-blink mode.</i><br><br>"
                "<i>(Observe for 10 seconds.)</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[1] or self.rtdcircuit_failed[1]:
            self.rtdcircuitlabel.setText(
                "9. Rotate the knob on IAS11003A counterclockwise until DMM reads 2.100 volts.<br><br>"
                "While monitoring the current drawn by the heaters, slowly rotate the knob until no current is drawn by the heaters (readings of ~0 A for each self.phase).<br><br>"
                "<i>The voltage on the DMM should be less than 2.060 volts.</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[2] or self.rtdcircuit_failed[2]:
            self.rtdcircuitlabel.setText(
                "10. Press the POWER button to turn off the Beverage Maker.<br><br>"
                "Set the red lever on the EDB to the OFF position.<br><br>"
                "11. Disconnect the IAS11003A from the controller board assy.<br><br>"
                "Connect the P4 to the controller board assy (J4).<br><br>"
                "12. Put the cover on the power module assy.<br><br>"
                "13. Set the red lever on the EDB to the ON position.<br><br>"
                "14. Press the power button.<br><br> "
                "<i>This should not trip the safety latch.</i><br>"
                "<i>(Make sure the power indicator light does not go into double-blink mode.)</i>"

            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[3] or self.rtdcircuit_failed[3] or self.current_rtdcircuit_step > 3:
            self.rtdcircuitlabel.setText(
                "<b>Test Complete.<br>"
                "The RTD Circuit Test has been completed successfully!<br><br>"
                "Please press the POWER button to turn off the Beverage Maker.</b><br><br>"
                )

            self.rtdcircuitbeginbutton.setText("Results")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuitResults)

            self.rtdcircuitrestart = QPushButton("Restart", self)
            self.rtdcircuitrestart.clicked.connect(self.RTDCircuitRestart)
            self.rtdcircuitrestart.setFixedWidth(200)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.rtdcircuitnext = QPushButton("Next", self)
            self.rtdcircuitnext.clicked.connect(self.RTDCircuitNext)
            self.rtdcircuitnext.setFixedWidth(200)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitnext,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def RTDCircuitNext(self):
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

    def RTDCircuitResults(self):
        print("Printing RTDCircuit Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/rtdcircuit"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "RTDCircuit has not been run yet.")
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
            "step1_rtdcircuit_doubleblink": "Safety Latch Trip & Double Blink Mode Test:",
            "step2_rtdcircuit_safetylatch": "Safety Latch Reset Verification Test:",
            "step3_rtdcircuit_voltage": "RTD Circuit Voltage Measurement (V):",
            "step4_rtdcircuit_safetylatchtrip": "Final Safety Latch Trip Verification Test:",
        }

        ordered_keys = [
            "step1_rtdcircuit_doubleblink",
            "step2_rtdcircuit_safetylatch",
            "step3_rtdcircuit_voltage",
            "step4_rtdcircuit_safetylatchtrip",
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
        report_lines.append("RTD Circuit Test")

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
        text = "<h2>RTD Circuit Results</h2>"
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
        win.setWindowTitle("RTD Circuit Results")
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

        self._rtdcircuit_results_window = win

    def RTDCircuitTestPath(self, path):
        self.test_path = path

    def insert_rtdcircuit_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>RTD Circuit Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("RTD Circuit section not found.")
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

    def RTDCircuitRestart(self):
        try:
            print("Restarting RTDCircuit Test")

            # ---------- State reset ----------
            self.rtdcircuit_results = ""
            self.rtdcircuit_passed = [False] * len(self.rtdcircuit_passed)
            self.rtdcircuit_failed = [False] * len(self.rtdcircuit_failed)
            self.rtdcircuit_completed = False
            self.current_rtdcircuit_step = 0
            self.step_status = {}

            # ---------- Restore instructions ----------
            self.rtdcircuitlabel.setText(
                "<b>1. With the Beverage Maker connected to the water supply and the red lever on the EDB in the OFF position,"
            " remove the cover from the power module assy and disconnect the RTD assy plug (P4) from the J4"
            " connector on the controller board assy.<br><br>"
            "2. Connect the DMM (set to ohms scale) to the RTD simulator harness (IAS11003A).<br><br>"
            "Rotate the knob until 1430±1 ohms is indicated on the DMM.<br><br>"
            "Change DMM to DC volts then connect harness inline between the controller board assy (J4) and P4.<br><br>"
            "3. Connect the Beverage Maker to the power supply.<br><br>"
            "Set the red lever on the EDB to the ON position.<br><br>"
            "4. Press the power button.<br><br>"
            "<i>This should trip the safety latch.</i><br><br>"
            "<i>(If the safety latch is tripped, there will be no current drawn to the heaters and the power indicator light should go into double-blink mode.)</i><br><br>"
            )

            # ---------- Remove completion buttons ----------
            if hasattr(self, "rtdcircuitrestart") and self.rtdcircuitrestart:
                self.rtdcircuittestbuttonlayout.removeWidget(self.rtdcircuitrestart)
                self.rtdcircuitrestart.deleteLater()
                self.rtdcircuitrestart = None

            if hasattr(self, "rtdcircuitnext") and self.rtdcircuitnext:
                self.rtdcircuittestbuttonlayout.removeWidget(self.rtdcircuitnext)
                self.rtdcircuitnext.deleteLater()
                self.rtdcircuitnext = None

            # ---------- Restore Begin button ----------
            self.rtdcircuitbeginbutton.setText("Begin")
            try:
                self.rtdcircuitbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        except Exception as e:
            print(f"Error restarting RTDCircuit Test: {e}")


    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[RTDCircuit] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

    def PostRTDCircuitResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("RTD Circuit: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/rtdcircuit"
            r = requests.post(url, json=payload, timeout=5)
            print("RTD Circuit POST status:", r.status_code)
            print("RTD Circuit POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting RTD Circuit result: {e}")

    def post_rtdcircuit_snapshot(self):
        """
        Compute an overall status from what we know so far and POST to the server.
        This can be called after each step so partial progress is saved.
        """
        # Overall status logic:
        # - If test not completed yet, call it "INCOMPLETE"
        # - If completed, PASS only if all tracked steps passed
        if not self.rtdcircuit_completed:
            overall_status = "INCOMPLETE"
        else:
            overall_status = "PASS" if all(self.rtdcircuit_passed) else "FAIL"

        data = {
            "steps": self.step_status,
            "completed": self.rtdcircuit_completed,
        }

        notes = ""  # or derive something from failures if you want

        self.PostRTDCircuitResults(status=overall_status, data=data, notes=notes)


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
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/rtdcircuit"
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
                self.current_rtdcircuit_step = 4
                print(f"Current step: {self.current_rtdcircuit_step}")
                self.updateRTDCircuitStep()

            elif status == "INCOMPLETE":
                steps = payload.get("data", {}).get("steps", {})
                # Resume at "next" step index
                self.current_rtdcircuit_step = len(steps)
                print(f"Current step: {self.current_rtdcircuit_step}")
                self.updateRTDCircuitStep()
                return

            self.updateRTDCircuitStep()

        except Exception as e:
            print(f"[RTDCircuit] sync_completed_from_db failed: {e}")