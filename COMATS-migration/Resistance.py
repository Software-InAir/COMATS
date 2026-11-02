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
        self.phaseAread = 0
        self.phaseBread = 0
        self.phaseCread = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.resistancelabellayout = QHBoxLayout()
        self.resistancetestbuttonlayout = QHBoxLayout()

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
        layout.addLayout(self.resistancetestbuttonlayout)
        try:
            self.resistancebeginbutton = QPushButton("Begin")
            self.resistancebeginbutton.setFixedWidth(200)
            self.resistancebeginbutton.clicked.connect(self.Resistance)
            self.resistancetestbuttonlayout.addWidget(self.resistancebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
                            self.post_resistance_snapshot()
                        else:
                            self.resistance_passed[2] = False
                            self.resistance_failed[2] = True
                            self.resistance_completed = True
                            self.post_resistance_snapshot()

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

        if self.resistance_passed[2] or self.resistance_failed[2] or self.current_resistance_step > 2:
            self.resistancelabel.setText(
                "<b>Resistance Test Completed!</b><br><br>"
                "<b>The Resistance Test has been completed successfully!</b><br><br>"
                "<b>Please Disconnect the IAS11003C plug from PP1 and turn off the milliohm meter.<br><br>"
            )
            self.resistancebeginbutton.setText("Results")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.ResistanceResults)

            self.resistancerestartbutton = QPushButton("Restart", self)
            self.resistancerestartbutton.clicked.connect(self.ResistanceRestart)
            self.resistancerestartbutton.setFixedWidth(200)
            self.resistancetestbuttonlayout.addWidget(self.resistancerestartbutton, alignment=Qt.AlignmentFlag.AlignCenter)

            self.resistancenextbutton = QPushButton("Next", self)
            self.resistancenextbutton.clicked.connect(self.ResistanceNext)
            self.resistancenextbutton.setFixedWidth(200)
            self.resistancetestbuttonlayout.addWidget(self.resistancenextbutton,
                                                            alignment=Qt.AlignmentFlag.AlignCenter)

    def ResistanceNext(self):
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

    def ResistanceResults(self):
        print("Printing Resistance Test Results")

        if self.test_id is None or self.api_base_url is None:
            QMessageBox.warning(self, "No Context", "Test context not set.")
            return

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/resistance"
            r = requests.get(url, timeout=5)

            if r.status_code == 404:
                QMessageBox.information(self, "No Results", "Resistance has not been run yet.")
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
            "step1_resistance_brewshelf": "Brew Shelf Ground Resistance Test (mΩ):",
            "step2_resistance_hotplate": "Platen Heater Ground Resistance Test (mΩ):",
            "step3_resistance_faucet": "Faucet Ground Resistance Test (mΩ):",
        }

        ordered_keys = [
            "step1_resistance_brewshelf",
            "step2_resistance_hotplate",
            "step3_resistance_faucet",
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
        report_lines.append("Resistance Test")

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
        text = "<h2>Resistance Results</h2>"
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
        win.setWindowTitle("Resistance Results")
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

        self._resistance_results_window = win

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
        try:
            print("Restarting Resistance Test")

            # ---------- State reset ----------
            self.resistance_results = ""
            self.resistance_passed = [False] * len(self.resistance_passed)
            self.resistance_failed = [False] * len(self.resistance_failed)
            self.resistance_completed = False
            self.current_resistance_step = 0
            self.step_status = {}

            # ---------- Restore instructions ----------
            self.resistancelabel.setText(
                "<b>Turn QuadTech Milliohm Meter on. <br><br>"
                "1. Check resistance from plug lead G to un-anodized brew shelf.</b><br><br> "
                "<i> The millohm meter should not exceed 4.5 milliohms. </i><br><br>"
            )

            # ---------- Remove completion buttons ----------
            if hasattr(self, "resistancerestart") and self.resistancerestart:
                self.resistancetestbuttonlayout.removeWidget(self.resistancerestart)
                self.resistancerestart.deleteLater()
                self.resistancerestart = None

            if hasattr(self, "resistancenext") and self.resistancenext:
                self.resistancetestbuttonlayout.removeWidget(self.resistancenext)
                self.resistancenext.deleteLater()
                self.resistancenext = None

            # ---------- Restore Begin button ----------
            self.resistancebeginbutton.setText("Begin")
            try:
                self.resistancebeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.resistancebeginbutton.clicked.connect(self.Resistance)

        except Exception as e:
            print(f"Error restarting Resistance Test: {e}")


    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[Resistance] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

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
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/resistance"
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
                self.current_resistance_step = 3
                print(f"Current step: {self.current_resistance_step}")
                self.updateResistanceStep()

            elif status == "INCOMPLETE":
                steps = payload.get("data", {}).get("steps", {})
                # Resume at "next" step index
                self.current_resistance_step = len(steps)
                print(f"Current step: {self.current_resistance_step}")
                self.updateResistanceStep()
                return

            self.updateResistanceStep()

        except Exception as e:
            print(f"[Resistance] sync_completed_from_db failed: {e}")

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