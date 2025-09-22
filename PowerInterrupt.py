from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- PowerInterrupt Check

class PowerInterruptTest(QWidget):

    def __init__(self):
        super().__init__()

        self.powerinterrupt_results = ""
        self.powerinterrupt_passed = [False, False, False, False]
        self.powerinterrupt_failed = [False, False, False, False]
        self.powerinterrupt_completed = False
        self.current_powerinterrupt_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.powerinterruptlabellayout = QHBoxLayout()
        self.powerinterrupttestbuttonlayout = QHBoxLayout()

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

        self.powerinterruptlabel = QLabel(
            "<b> During a brew cycle turn off the Coffee Maker by pressing ON/OFF, then quickly turn it back on by pressing ON/OFF again. <br><br>"
                  "<i> Verify that the BREW light remains on.  </i><br><br>"

        )

        self.powerinterruptlabel.setTextFormat(Qt.TextFormat.RichText)
        self.powerinterruptlabel.setWordWrap(True)
        self.powerinterruptlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.powerinterruptlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.powerinterruptlabel)


        self.powerinterruptlabellayout.addWidget(scroll)
        layout.addLayout(self.powerinterruptlabellayout)
        layout.addLayout(self.powerinterrupttestbuttonlayout)
        try:
            self.powerinterruptbeginbutton = QPushButton("Begin")
            self.powerinterruptbeginbutton.setFixedWidth(200)
            self.powerinterruptbeginbutton.clicked.connect(self.PowerInterrupt)
            self.powerinterrupttestbuttonlayout.addWidget(self.powerinterruptbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(powerinterrupt, f"PowerInterrupt")

    def PowerInterrupt(self):
        try:
            msg1 = QMessageBox()

            if self.current_powerinterrupt_step == 0:
                msg1.setWindowTitle("Brew Light")
                msg1.setText("The Brew Indicator Light remains illuminated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Power Interrupt Test: "
                    result_line += "\tPASS"
                    self.insert_powerinterrupt_result(result_line)
                    self.powerinterrupt_passed[0] = True
                    self.powerinterrupt_failed[0] = False
                    self.powerinterrupt_completed = True
                    self.updatePowerInterruptStep()
                    self.current_powerinterrupt_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Power Interrupt Test: "
                    result_line += "\tFAIL"
                    self.insert_powerinterrupt_result(result_line)
                    self.powerinterrupt_passed[0] = False
                    self.powerinterrupt_failed[0] = True
                    self.powerinterrupt_completed = True
                    self.updatePowerInterruptStep()




            # Completed
            elif self.powerinterrupt_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Power Interrupt test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updatePowerInterruptStep()

        except Exception as e:
            print(f"Error: {e}")

    def updatePowerInterruptStep(self):

        if self.powerinterrupt_passed[0] or self.powerinterrupt_failed[0]:
            print("Update Power Interrupt Step")
            self.powerinterruptlabel.setText(
                "  <i> The LOW WATER lamp should turn off once tank is full. </i><br><br>"

            )
            self.powerinterruptbeginbutton.setText("Continue")
            self.powerinterruptbeginbutton.clicked.disconnect()
            self.powerinterruptbeginbutton.clicked.connect(self.PowerInterrupt)

        if self.powerinterrupt_passed[1] or self.powerinterrupt_failed[1]:
            print("Update Power Interrupt Step")
            self.powerinterruptlabel.setText(
                " <b>  Each heater should draw approximately 8±1 amps</b> <br><br>"
                " <i>  Please enter the amperage of Phase A as displayed by the phase readings window </i><br><br>"
            )
            self.powerinterruptbeginbutton.setText("Continue")
            self.powerinterruptbeginbutton.clicked.disconnect()
            self.powerinterruptbeginbutton.clicked.connect(self.PowerInterrupt)


        if self.powerinterrupt_completed == True:
            self.powerinterruptlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Power Interrupt test has been completed successfully!</b><br><br>"
            )
            self.powerinterruptbeginbutton.setText("Results")
            self.powerinterruptbeginbutton.clicked.disconnect()
            self.powerinterruptbeginbutton.clicked.connect(self.PowerInterruptResults)

            self.powerinterruptrestart = QPushButton("Restart", self)
            self.powerinterruptrestart.clicked.connect(self.PowerInterruptRestart)
            self.powerinterruptrestart.setFixedWidth(200)
            self.powerinterrupttestbuttonlayout.addWidget(self.powerinterruptrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetPowerInterruptResults(self):
        return self.powerinterrupt_results

    def PowerInterruptTestPath(self, path):
        self.test_path = path

    def insert_powerinterrupt_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Power Interrupt Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Power Interrupt section not found.")
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

    def PowerInterruptRestart(self):
        print("Restarting Power Interrupt Test")

    def PowerInterruptResults(self):
        print("Printing Power Interrupt Test Results")