from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- PressureReliefValve Check

class PressureReliefValveTest(QWidget):

    def __init__(self):
        super().__init__()

        self.pressurereliefvalve_results = ""
        self.pressurereliefvalve_passed = [False, False, False, False]
        self.pressurereliefvalve_failed = [False, False, False, False]
        self.pressurereliefvalve_completed = False
        self.current_pressurereliefvalve_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

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
            "<b>Remove brew cup assembly and dry off before starting. <br><br>"
            "Close V10 then turn V8 vertical. <br><br>"
            "Connect the Coffee Maker to water supply and then open V10. <br><br>"
            "Let tank fill with water, FM will go to zero when full. <br><br>"
            "With water tank full, increase source water pressure by rotating V7 clockwise until PG2 reads between 90 psig and 100 psig, venting V9 periodically. <br><br>"
            "Verify the pressure relief valve opens indicated by water dripping in brew cup assembly housing. </b><br><br>"
            "<i>Make sure that the pressure relief valve opens at 95±10 PSIG, if not replace the pressure relief valve.</i> <br><br>"

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
        phaselayout = QHBoxLayout()

        spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer1)

        spacer2 = QSpacerItem(800, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        phaselayout.addSpacerItem(spacer2)

        phase1 = QLabel("Phase 1:")
        phaselayout.addWidget(phase1)

        phase1reading = QLabel(f"{phase1read}")
        phaselayout.addWidget(phase1reading)

        phase2 = QLabel("Phase 2:")
        phaselayout.addWidget(phase2)

        phase2reading = QLabel(f"{phase2read}")
        phaselayout.addWidget(phase2reading)

        phase3 = QLabel("Phase 3")
        phaselayout.addWidget(phase3)

        phase3reading = QLabel(f"{phase3read}")
        phaselayout.addWidget(phase3reading)

        layout.addLayout(phaselayout)

        self.setLayout(layout)
        #tabs.addTab(pressurereliefvalve, f"PressureReliefValve")

    def PressureReliefValve(self):
        try:

            msg1 = QMessageBox()

            if self.current_pressurereliefvalve_step == 0:
                value1, ok = QInputDialog.getDouble(
                    self,
                    "Pressure Relief Valve",
                    "Please enter the pressure with which the Pressure Relief Valve opens",
                    decimals=2,
                    min=0.0,
                    max=200.0,
                    step=.01
                )
                self.pressurereliefvalve_results += f""
                if ok:
                    result_line = f"Pressure Relief Valve Operational Pressure: {value1} PSIG \n"
                    if value1 >= 85 and value1 <= 105:
                        result_line += "\tPASS"
                        self.pressurereliefvalve_passed[0] = True
                        self.pressurereliefvalve_failed[0] = False
                    else:
                        result_line += "\tFAIL"
                        self.pressurereliefvalve_passed[0] = False
                        self.pressurereliefvalve_failed[0] = True

                    self.insert_pressurereliefvalve_result(result_line)
                    self.current_pressurereliefvalve_step += 1
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
                    self.insert_pressurereliefvalve_result(result_line)
                    self.pressurereliefvalve_passed[1] = True
                    self.pressurereliefvalve_failed[1] = False
                    self.current_pressurereliefvalve_step += 1
                    self.updatePressureReliefValveStep()


                elif msg1.clickedButton() == fail_button:
                    result_line = f"Pressure Relief Valve Leak Check: "
                    result_line += "\tFAIL"
                    self.insert_pressurereliefvalve_result(result_line)
                    self.pressurereliefvalve_passed[1] = False
                    self.pressurereliefvalve_failed[1] = True
                    self.updatePressureReliefValveStep()


            elif self.current_pressurereliefvalve_step == 2:
                value1, ok = QInputDialog.getDouble(
                    self,
                    "Vented Relief Pressure",
                    "Please enter the pressure observed on PG2 after venting",
                    decimals=2,
                    min=0.0,
                    max=100.0,
                    step=.01
                )
                self.pressurereliefvalve_results += f""
                if ok:
                    result_line = f"Vented Pressure: {value1} PSIG \n"
                    if value1 <= 30:
                        result_line += "\tPASS"
                        self.pressurereliefvalve_passed[2] = True
                        self.pressurereliefvalve_failed[2] = False
                    else:
                        result_line += "\tFAIL"
                        self.pressurereliefvalve_passed[2] = False
                        self.pressurereliefvalve_failed[2] = True

                    self.insert_pressurereliefvalve_result(result_line)
                    self.current_pressurereliefvalve_step += 1
                    self.pressurereliefvalve_completed = True
                    self.updatePressureReliefValveStep()

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

        if self.pressurereliefvalve_passed[0] or self.pressurereliefvalve_failed[0]:
            print("Update Pressure Relief Valve Step")
            self.pressurereliefvalvelabel.setText(
                "Check for leaks after 5 minutes. <br><br>"
                "<i>No leaks are to be observed </i><br><br>"
            )
            self.pressurereliefvalvebeginbutton.setText("Continue")
            self.pressurereliefvalvebeginbutton.clicked.disconnect()
            self.pressurereliefvalvebeginbutton.clicked.connect(self.PressureReliefValve)

        if self.pressurereliefvalve_passed[1] or self.pressurereliefvalve_failed[1]:
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


        if self.pressurereliefvalve_completed == True:
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

    def GetPressureReliefValveResults(self):
        return self.pressurereliefvalve_results

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
        print("Restarting Pressure Relief Valve Test")

    def PressureReliefValveResults(self):
        print("Printing Pressure Relief Valve Test Results")