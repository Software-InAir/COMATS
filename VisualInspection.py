from PyQt6 import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy,
                             QPushButton, QMessageBox, QCheckBox, QTabWidget, QMainWindow, QComboBox)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, pyqtSlot, QUrl

from InstrumentWorker import InstrumentWorker

import requests
import subprocess
import platform
import os
import sys

from pathlib import Path


#------------------------------------------------------- VisualInspection Check

class VisualInspectionTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker | None = None, tabs: QTabWidget | None = None, parent=None):
        super().__init__()
        self.instrument = instrument_worker
        self.tabs = tabs

        self.test_id: int | None = None
        self.api_base_url: str | None = None
        self.web = None

        # -------- temp phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0


        self.current_visualinspection_step = 0

        layout = QVBoxLayout()

        self.visualinspectionlayout = QHBoxLayout()
        self.visualinspectionlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visualinspectionlabellayout = QVBoxLayout()
        self.visualinspectionlabellayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.visualinspectionchecklayout = QVBoxLayout()
        self.visualinspectionchecklayout.setContentsMargins(0, 0, 0, 0)
        self.visualinspectionchecklayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.visualinspectiontestbuttonlayout = QHBoxLayout()


        self.visualinspectionlabel = QLabel(
            "<b>1. Inspect Coffee Maker for physical damage and verify all parts are present and secure.<br>"
            "   2. Inspect power connector P2 for damage, verify pins are straight and not excessively worn.<br>"
            "   3. Inspect water inlet plug for damage and/or contamination.<br>"
            "   4. Inspect bottom of Coffee Maker to verify all wires are properly tied, "
            "   and that the Coffee Maker is free of obstruction to installation.<br>"
            "   5. Check rail supports for straightness.<br>"
            "   6. Check brew handle for proper operation.<br>"
            "   7. Inspect switch lens caps for cracks, marks, or illegible printing.<br><br>"
            "   Electrical Enclosure:<br>"
            "   1. Check that all parts are present and undamaged.<br>"
            "   2. Check terminal block attachments for tightness.<br>"
            "   3. Check that wires are undamaged, secured and routed out of the way as much as possible.<br>"
            "   4. Check connector J1 for damaged contacts and good solder joints.<br>"
            "   5. Inspect relay socket for corrosion or overheated wires.<br>"
            "   6. Check the circuit breaker CB1 for proper operation.</b><br>"
            "<i></i><br><br>"
            )

        self.visualinspectionlabel.setTextFormat(Qt.TextFormat.RichText)
        self.visualinspectionlabel.setWordWrap(True)
        self.visualinspectionlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 45px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.visualinspectionlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.checkList1 = QCheckBox()
        self.checkList1.setStyleSheet("""
                                padding-top: 55px;
                                margin-bottom: 20px;
                                """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList1)
        self.checkList2 = QCheckBox()
        self.checkList2.setStyleSheet("""
                                        margin-bottom: 20px;
                                        """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList2)
        self.checkList3 = QCheckBox()
        self.checkList3.setStyleSheet("""
                                        margin-bottom: 0px;
                                        """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList3)
        self.checkList4 = QCheckBox()
        self.checkList4.setStyleSheet("""
                                        margin-bottom: 40px;
                                        """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList4)
        self.checkList5 = QCheckBox()
        self.checkList5.setStyleSheet("""
                                        margin-bottom: 0px;
                                        """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList5)
        self.checkList6 = QCheckBox()
        self.checkList6.setStyleSheet("""
                                        margin-bottom: 0px;
                                        """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList6)
        self.checkList7 = QCheckBox()
        self.checkList7.setStyleSheet("""
                                        margin-bottom: 50px;
                                        """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList7)
        self.checkList8 = QCheckBox()
        self.checkList8.setStyleSheet("""
                                                margin-bottom: 0px;
                                                """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList8)
        self.checkList9 = QCheckBox()
        self.checkList9.setStyleSheet("""
                                                margin-bottom: 0px;
                                                """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList9)
        self.checkList10 = QCheckBox()
        self.checkList10.setStyleSheet("""
                                                margin-bottom: 30px;
                                                """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList10)
        self.checkList11 = QCheckBox()
        self.checkList11.setStyleSheet("""
                                                margin-bottom: 0px;
                                                """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList11)
        self.checkList12 = QCheckBox()
        self.checkList12.setStyleSheet("""
                                                margin-bottom: 0px;
                                                """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList12)
        self.checkList13 = QCheckBox()
        self.checkList13.setStyleSheet("""
                                                margin-bottom: 0px;
                                                """
                                      )
        self.visualinspectionchecklayout.addWidget(self.checkList13)


        self.visualinspectionlabellayout.addWidget(self.visualinspectionlabel)

        self.visualinspectionlayout.addLayout(self.visualinspectionlabellayout)
        self.visualinspectionlayout.addLayout(self.visualinspectionchecklayout)


        layout.addLayout(self.visualinspectionlayout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(self.visualinspectiontestbuttonlayout)

        self.adjustSize()


        self.visualinspectionbeginbutton = QPushButton("Submit Inspection")
        self.visualinspectionbeginbutton.setFixedWidth(200)
        self.visualinspectionbeginbutton.clicked.connect(self.VisualInspection)
        self.visualinspectiontestbuttonlayout.addWidget(self.visualinspectionbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)


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

    def VisualInspection(self):
        try:
            msg1 = QMessageBox()

            if self.current_visualinspection_step == 0:
                if self.checkList1.isChecked() and self.checkList2.isChecked() and self.checkList3.isChecked() and self.checkList4.isChecked() and self.checkList5.isChecked() and self.checkList6.isChecked() \
                    and self.checkList7.isChecked() and self.checkList8.isChecked() and self.checkList9.isChecked() and self.checkList10.isChecked() and self.checkList11.isChecked() \
                    and self.checkList12.isChecked() and self.checkList13.isChecked():
                    result_line = f"Visual Inspection:"
                    result_line += "\t\t\t\t\t\t\t\t\t\t\t\t\t\tPASS"
                else:
                    result_line = f"Visual Inspection:"
                    result_line += "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tFAIL\n"

                all_ok = (
                        self.checkList1.isChecked() and
                        self.checkList2.isChecked() and
                        self.checkList3.isChecked() and
                        self.checkList4.isChecked() and
                        self.checkList5.isChecked() and
                        self.checkList6.isChecked() and
                        self.checkList7.isChecked() and
                        self.checkList8.isChecked() and
                        self.checkList9.isChecked() and
                        self.checkList10.isChecked() and
                        self.checkList11.isChecked() and
                        self.checkList12.isChecked() and
                        self.checkList13.isChecked()
                )

                status = "PASS" if all_ok else "FAIL"

                failures = []



                if not self.checkList1.isChecked():
                    result_line += "Physical Damage or Missing Parts\n"
                    failures.append("Physical Damage or Missing Parts")

                if not self.checkList2.isChecked():
                    result_line += "Power Connector P2 Damage\n"
                    failures.append("Power Connector P2 Damage")

                if not self.checkList3.isChecked():
                    result_line += "Water Inlet Plug Damage\n"
                    failures.append("Water Inlet Plug Damage")

                if not self.checkList4.isChecked():
                    result_line += "Improperly Tied Wiring\n"
                    failures.append("Improperly Tied Wiring")

                if not self.checkList5.isChecked():
                    result_line += "Bent Rail Supports\n"
                    failures.append("Bent Rail Supports")

                if not self.checkList6.isChecked():
                    result_line += "Brew Handle Damage\n"
                    failures.append("Brew Handle Damage")

                if not self.checkList7.isChecked():
                    result_line += "Switch Lens Damage\n"
                    failures.append("Switch Lens Damage")

                if not self.checkList8.isChecked():
                    result_line += "Electrical Enclosure Damage or Missing Parts\n"
                    failures.append("Electrical Enclosure Damage or Missing Parts")

                if not self.checkList9.isChecked():
                    result_line += "Loose Terminal Blocks\n"
                    failures.append("Loose Terminal Blocks")

                if not self.checkList10.isChecked():
                    result_line += "Damaged Electrical Enclosure Wiring\n"
                    failures.append("Damaged Electrical Enclosure Wiring")

                if not self.checkList11.isChecked():
                    result_line += "Connector J1 Damage\n"
                    failures.append("Connector J1 Damage")

                if not self.checkList12.isChecked():
                    result_line += "Relay Socket Damage or Corrosion\n"
                    failures.append("Relay Socket Damage or Corrosion")

                if not self.checkList13.isChecked():
                    result_line+= "Circuit Breaker CB1 Damage\n"
                    failures.append("Circuit Breaker CB1 Damage")

                data = {
                    "all_checks_passed": all_ok,

                    # per-item booleans
                    "check1_physical_ok": self.checkList1.isChecked(),
                    "check2_p2_ok": self.checkList2.isChecked(),
                    "check3_inlet_plug_ok": self.checkList3.isChecked(),
                    "check4_wiring_ok": self.checkList4.isChecked(),
                    "check5_rails_ok": self.checkList5.isChecked(),
                    "check6_brew_handle_ok": self.checkList6.isChecked(),
                    "check7_switch_lens_ok": self.checkList7.isChecked(),
                    "check8_enclosure_ok": self.checkList8.isChecked(),
                    "check9_terminal_blocks_ok": self.checkList9.isChecked(),
                    "check10_wiring_ok": self.checkList10.isChecked(),
                    "check11_j1_ok": self.checkList11.isChecked(),
                    "check12_relay_socket_ok": self.checkList12.isChecked(),
                    "check13_cb1_ok": self.checkList13.isChecked(),

                    "failures": failures,
                }

                notes = "" if all_ok else "; ".join(failures)

                self.PostVisualInspectionResults(status=status, data=data, notes=notes)

                self.current_visualinspection_step += 1
                self.insert_visualinspection_result(result_line)
                msg1.setWindowTitle("Visual Inspection Results")
                msg1.setText("Visual Inspection Results have been updated.")
                msg1.exec()
                self.updateVisualInspectionStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateVisualInspectionStep(self):
        if self.current_visualinspection_step == 1:
            self.visualinspectionlabel.setText(
                "<b>Step Complete.</b><br><br>"
                "<i>Visual Inspection Step has been Completed Successfully.</i><br><br>"
                )

            while self.visualinspectionchecklayout.count():
                child = self.visualinspectionchecklayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.visualinspectionbeginbutton.setText("Results")
            self.visualinspectionbeginbutton.clicked.disconnect()
            self.visualinspectionbeginbutton.clicked.connect(self.VisualInspectionResults)

            self.visualinspectionrestart = QPushButton("Restart", self)
            self.visualinspectionrestart.clicked.connect(self.VisualInspectionRestart)
            self.visualinspectionrestart.setFixedWidth(200)
            self.visualinspectiontestbuttonlayout.addWidget(self.visualinspectionrestart, alignment=Qt.AlignmentFlag.AlignCenter)

            self.visualinspectionnext = QPushButton("Next", self)
            self.visualinspectionnext.clicked.connect(self.VisualInspectionNext)
            self.visualinspectionnext.setFixedWidth(200)
            self.visualinspectiontestbuttonlayout.addWidget(self.visualinspectionnext, alignment=Qt.AlignmentFlag.AlignCenter)

    def VisualInspectionNext(self):
        current =self.tabs.currentIndex()
        self.tabs.setCurrentIndex(current+1)


    def VisualInspectionTestPath(self, path):
        self.test_path = path

    def insert_visualinspection_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Visual Inspection Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Visual Inspection section not found.")
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

    def VisualInspectionRestart(self):
        try:
            print("Restarting Test")

            # Reset state
            self.current_visualinspection_step = 0

            # Restore instructions (keep your existing HTML)
            self.visualinspectionlabel.setText(
                "<b>1. Inspect Coffee Maker for physical damage and verify all parts are present and secure.<br>"
                "   2. Inspect power connector P2 for damage, verify pins are straight and not excessively worn.<br>"
                "   3. Inspect water inlet plug for damage and/or contamination.<br>"
                "   4. Inspect bottom of Coffee Maker to verify all wires are properly tied, "
                "   and that the Coffee Maker is free of obstruction to installation.<br>"
                "   5. Check rail supports for straightness.<br>"
                "   6. Check brew handle for proper operation.<br>"
                "   7. Inspect switch lens caps for cracks, marks, or illegible printing.<br><br>"
                "   Electrical Enclosure:<br>"
                "   1. Check that all parts are present and undamaged.<br>"
                "   2. Check terminal block attachments for tightness.<br>"
                "   3. Check that wires are undamaged, secured and routed out of the way as much as possible.<br>"
                "   4. Check connector J1 for damaged contacts and good solder joints.<br>"
                "   5. Inspect relay socket for corrosion or overheated wires.<br>"
                "   6. Check the circuit breaker CB1 for proper operation.</b><br>"
                "<i></i><br><br>"
            )

            # --- 1) Remove "complete screen" buttons if they exist ---
            if hasattr(self, "visualinspectionrestart") and self.visualinspectionrestart:
                self.visualinspectiontestbuttonlayout.removeWidget(self.visualinspectionrestart)
                self.visualinspectionrestart.deleteLater()
                self.visualinspectionrestart = None

            if hasattr(self, "visualinspectionnext") and self.visualinspectionnext:
                self.visualinspectiontestbuttonlayout.removeWidget(self.visualinspectionnext)
                self.visualinspectionnext.deleteLater()
                self.visualinspectionnext = None

            # --- 2) Clear old checklist widgets FIRST (this is the key fix) ---
            while self.visualinspectionchecklayout.count():
                child = self.visualinspectionchecklayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # --- 3) Rebuild the checklist ---
            self.checkList1 = QCheckBox()
            self.checkList1.setStyleSheet("padding-top: 55px; margin-bottom: 20px;")
            self.visualinspectionchecklayout.addWidget(self.checkList1)

            self.checkList2 = QCheckBox()
            self.checkList2.setStyleSheet("margin-bottom: 20px;")
            self.visualinspectionchecklayout.addWidget(self.checkList2)

            self.checkList3 = QCheckBox()
            self.checkList3.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList3)

            self.checkList4 = QCheckBox()
            self.checkList4.setStyleSheet("margin-bottom: 40px;")
            self.visualinspectionchecklayout.addWidget(self.checkList4)

            self.checkList5 = QCheckBox()
            self.checkList5.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList5)

            self.checkList6 = QCheckBox()
            self.checkList6.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList6)

            self.checkList7 = QCheckBox()
            self.checkList7.setStyleSheet("margin-bottom: 50px;")
            self.visualinspectionchecklayout.addWidget(self.checkList7)

            self.checkList8 = QCheckBox()
            self.checkList8.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList8)

            self.checkList9 = QCheckBox()
            self.checkList9.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList9)

            self.checkList10 = QCheckBox()
            self.checkList10.setStyleSheet("margin-bottom: 30px;")
            self.visualinspectionchecklayout.addWidget(self.checkList10)

            self.checkList11 = QCheckBox()
            self.checkList11.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList11)

            self.checkList12 = QCheckBox()
            self.checkList12.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList12)

            self.checkList13 = QCheckBox()
            self.checkList13.setStyleSheet("margin-bottom: 0px;")
            self.visualinspectionchecklayout.addWidget(self.checkList13)

            # --- 4) Restore begin button (don't recreate it; just reset it) ---
            self.visualinspectionbeginbutton.setText("Submit Inspection")
            try:
                self.visualinspectionbeginbutton.clicked.disconnect()
            except TypeError:
                pass
            self.visualinspectionbeginbutton.clicked.connect(self.VisualInspection)

        except Exception as e:
            print(f"Error restarting: {e}")

    def VisualInspectionResults(self):
        print("Printing VisualInspection Test Results")

    def set_test_context(self, test_id: int, api_base_url: str):
        self.test_id = test_id
        self.api_base_url = api_base_url.rstrip("/")
        print(f"[VisualInspection] Context set: test_id={self.test_id}, api_base_url={self.api_base_url}")

        self.SubtestsCompleted()

    def PostVisualInspectionResults(self, status: str, data: dict, notes: str):
        if self.test_id is None or self.api_base_url is None:
            print("Visual Inspection: Test Context not set; skipping Post")
            return

        payload = {
            "status": status,
            "data": data,
            "notes": notes,
        }

        try:
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/visualinspection"
            r = requests.post(url, json=payload, timeout=5)
            print("Visual Inspection POST status:", r.status_code)
            print("Visual Inspection POST body:", repr(r.text))
            r.raise_for_status()
        except Exception as e:
            print(f"Error posting Visual Inspection result: {e}")

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
            url = f"{self.api_base_url}/tests/{self.test_id}/subtests/visualinspection"
            r = requests.get(url, timeout=3)

            if r.status_code == 404:
                return  # not run yet

            r.raise_for_status()

            # If a row exists, treat as completed (status may be wrong for now)
            self.current_visualinspection_step = 1
            self.updateVisualInspectionStep()

        except Exception as e:
            print(f"[VisualInspection] sync_completed_from_db failed: {e}")




