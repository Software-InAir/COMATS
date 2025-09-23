from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal

from InstrumentWorker import InstrumentWorker





class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- HeaterCurrent Check

class HeaterCurrentTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker, parent=None):
        super().__init__()

        self.instrument = instrument_worker

        self.heatercurrent_results = ""
        self.heatercurrent_passed = [False, False, False, False]
        self.heatercurrent_failed = [False, False, False, False]
        self.heatercurrent_completed = False
        self.current_heatercurrent_step = 0

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

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
        self.phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.phaselayout.addSpacerItem(spacer2)

        self.phase1 = QLabel("Phase 1:")
        self.phaselayout.addWidget(self.phase1)

        self.phase1reading = QLabel(f"{self.phase1read}")
        self.phaselayout.addWidget(self.phase1reading)

        self.phase2 = QLabel("Phase 2:")
        self.phaselayout.addWidget(self.phase2)

        self.phase2reading = QLabel(f"{self.phase2read}")
        self.phaselayout.addWidget(self.phase2reading)

        self.phase3 = QLabel("Phase 3")
        self.phaselayout.addWidget(self.phase3)

        self.phase3reading = QLabel(f"{self.phase3read}")
        self.phaselayout.addWidget(self.phase3reading)

        layout.addLayout(self.phaselayout)

        self.setLayout(layout)
        #tabs.addTab(heatercurrent, f"HeaterCurrent")

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
                    self.heatercurrent_passed[0] = True
                    self.heatercurrent_failed[0] = False
                    self.heatercurrent_completed = True
                    self.updateHeaterCurrentStep()
                    self.current_heatercurrent_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Flow Meter Test: "
                    result_line += "\tFAIL"
                    self.insert_heatercurrent_result(result_line)
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
                    self.heatercurrent_passed[1] = True
                    self.heatercurrent_failed[1] = False
                    self.heatercurrent_completed = True
                    self.updateHeaterCurrentStep()
                    self.current_heatercurrent_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"LOW Indicator Light Test: "
                    result_line += "\tFAIL"
                    self.insert_heatercurrent_result(result_line)
                    self.heatercurrent_passed[1] = False
                    self.heatercurrent_failed[1] = True
                    self.updateHeaterCurrentStep()
                    self.current_heatercurrent_step += 1

                msg1 = QMessageBox()
                # msg1.setIcon(QMessageBox.Icon.Information)

                if self.current_heatercurrent_step == 2:
                    value1, ok = QInputDialog.getDouble(
                        self,
                        "Phase A",
                        "Please enter the current of Phase A as displayed by the self.phase readings window.",
                        decimals=2,
                        min=0.0,
                        max=50.0,
                        step=.01
                    )
                    self.heatercurrent_results += f"Phase A: {value1} A\n"
                    if ok:
                        result_line = f"Phase A: {value1} A"
                        if value1 >= 7 and value1 <= 9:   #----------------------------------------- Check these limits.
                            result_line += "\tPASS"
                            self.heatercurrent_passed[1] = True
                            self.heatercurrent_failed[1] = False
                        else:
                            result_line += "\tFAIL"
                            self.heatercurrent_passed[1] = False
                            self.heatercurrent_failed[1] = True
                        self.insert_heatercurrent_result(result_line)
                        self.current_heatercurrent_step += 1

                        if self.current_heatercurrent_step == 3:
                            value1, ok = QInputDialog.getDouble(
                                self,
                                "Phase B",
                                "Please enter the current of Phase B as displayed by the self.phase readings window.",
                                decimals=2,
                                min=0.0,
                                max=50.0,
                                step=.01
                            )
                            self.heatercurrent_results += f"Phase B: {value1} A\n"
                            if ok:
                                result_line = f"Phase B: {value1} A"
                                if value1 >= 7 and value1 <= 9:  # ----------------------------------------- Check these limits.
                                    result_line += "\tPASS"
                                    self.heatercurrent_passed[2] = True
                                    self.heatercurrent_failed[2] = False
                                else:
                                    result_line += "\tFAIL"
                                    self.heatercurrent_passed[2] = False
                                    self.heatercurrent_failed[2] = True
                                self.insert_heatercurrent_result(result_line)
                                self.current_heatercurrent_step += 1



                                if self.current_heatercurrent_step == 4:
                                    value1, ok = QInputDialog.getDouble(
                                        self,
                                        "Phase C",
                                        "Please enter the current of Phase C as displayed by the self.phase readings window.",
                                        decimals=2,
                                        min=0.0,
                                        max=50.0,
                                        step=.01
                                    )
                                    self.heatercurrent_results += f"Phase C: {value1} A\n"
                                    if ok:
                                        result_line = f"Phase C: {value1} A"
                                        if value1 >= 7 and value1 <= 9:  # ----------------------------------------- Check these limits.
                                            result_line += "\tPASS"
                                            self.heatercurrent_passed[3] = True
                                            self.heatercurrent_failed[3] = False
                                        else:
                                            result_line += "\tFAIL"
                                            self.heatercurrent_passed[3] = False
                                            self.heatercurrent_failed[3] = True
                                        self.insert_heatercurrent_result(result_line)
                                        self.updateHeaterCurrentStep()
                                        self.current_heatercurrent_step += 1



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

        if self.heatercurrent_passed[0] or self.heatercurrent_failed[0]:
            print("Update Heater Current Step")
            self.heatercurrentlabel.setText(
                "  <i> The LOW WATER lamp should turn off once tank is full. </i><br><br>"

            )
            self.heatercurrentbeginbutton.setText("Continue")
            self.heatercurrentbeginbutton.clicked.disconnect()
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrent)

        if self.heatercurrent_passed[1] or self.heatercurrent_failed[1]:
            print("Update Heater Current Step")
            self.heatercurrentlabel.setText(
                " <b>  Each heater should draw approximately 8±1 amps</b> <br><br>"
                " <i>  Please enter the amperage of Phase A as displayed by the self.phase readings window </i><br><br>"
            )
            self.heatercurrentbeginbutton.setText("Continue")
            self.heatercurrentbeginbutton.clicked.disconnect()
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrent)


        if self.heatercurrent_passed[2] or self.heatercurrent_failed[2]:
            self.heatercurrentlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Heater Current test has been completed successfully!</b><br><br>"
            )
            self.heatercurrentbeginbutton.setText("Results")
            self.heatercurrentbeginbutton.clicked.disconnect()
            self.heatercurrentbeginbutton.clicked.connect(self.HeaterCurrentResults)

            self.heatercurrentrestart = QPushButton("Restart", self)
            self.heatercurrentrestart.clicked.connect(self.HeaterCurrentRestart)
            self.heatercurrentrestart.setFixedWidth(200)
            self.heatercurrenttestbuttonlayout.addWidget(self.heatercurrentrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetHeaterCurrentResults(self):
        return self.heatercurrent_results

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
        print("Restarting HeaterCurrent Test")

    def HeaterCurrentResults(self):
        print("Printing HeaterCurrent Test Results")