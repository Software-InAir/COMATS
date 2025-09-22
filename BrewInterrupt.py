from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- BrewInterrupt Check

class BrewInterruptTest(QWidget):

    def __init__(self):
        super().__init__()

        self.brewinterrupt_results = ""
        self.brewinterrupt_passed = [False, False, False, False]
        self.brewinterrupt_failed = [False, False, False, False]
        self.brewinterrupt_completed = False
        self.current_brewinterrupt_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.brewinterruptlabellayout = QHBoxLayout()
        self.brewinterrupttestbuttonlayout = QHBoxLayout()

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

        self.brewinterruptlabel = QLabel(
            "<b>During a brew cycle raise the brew handle.</b><br><br>"
            "<i>The BREW light should deactivate.</i><br><br>"

        )

        self.brewinterruptlabel.setTextFormat(Qt.TextFormat.RichText)
        self.brewinterruptlabel.setWordWrap(True)
        self.brewinterruptlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.brewinterruptlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.brewinterruptlabel)


        self.brewinterruptlabellayout.addWidget(scroll)
        layout.addLayout(self.brewinterruptlabellayout)
        layout.addLayout(self.brewinterrupttestbuttonlayout)
        try:
            self.brewinterruptbeginbutton = QPushButton("Begin")
            self.brewinterruptbeginbutton.setFixedWidth(200)
            self.brewinterruptbeginbutton.clicked.connect(self.BrewInterrupt)
            self.brewinterrupttestbuttonlayout.addWidget(self.brewinterruptbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(brewinterrupt, f"BrewInterrupt")

    def BrewInterrupt(self):
        try:
            msg1 = QMessageBox()

            if self.current_brewinterrupt_step == 0:
                msg1.setWindowTitle("Brew Light")
                msg1.setText("The Brew Indicator Light deactivated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Brew Interrupt Test: "
                    result_line += "\tPASS"
                    self.insert_brewinterrupt_result(result_line)
                    self.brewinterrupt_passed[0] = True
                    self.brewinterrupt_failed[0] = False
                    self.updateBrewInterruptStep()
                    self.current_brewinterrupt_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Brew Interrupt Test: "
                    result_line += "\tFAIL"
                    self.insert_brewinterrupt_result(result_line)
                    self.brewinterrupt_passed[0] = False
                    self.brewinterrupt_failed[0] = True
                    self.updateBrewInterruptStep()



            elif self.current_brewinterrupt_step == 1:
                value1, ok = QInputDialog.getDouble(
                    self,
                    "Brew Flow",
                    "Please enter the flow rate indicated on FM",
                    decimals=2,
                    min=0.0,
                    max=200.0,
                    step=.01
                )
                self.brewinterrupt_results += f""
                if ok:
                    result_line = f"Brew Flow: {value1}GPM \n"
                    if value1 == 0:
                        result_line += "\tPASS"
                        self.brewinterrupt_passed[1] = True
                        self.brewinterrupt_failed[1] = False
                    else:
                        result_line += "\tFAIL"
                        self.brewinterrupt_passed[1] = False
                        self.brewinterrupt_failed[1] = True

                    self.insert_brewinterrupt_result(result_line)
                    self.current_brewinterrupt_step += 1
                    self.brewinterrupt_completed = True
                    self.updateBrewInterruptStep()




            # Completed
            elif self.brewinterrupt_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Brew Interrupt test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateBrewInterruptStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateBrewInterruptStep(self):

        if self.brewinterrupt_passed[0] or self.brewinterrupt_failed[0]:
            print("Update Brew Interrupt Step")
            self.brewinterruptlabel.setText(
                 "<i>The brew flow should cease as indicated by a value of zero indicated on FM.</i> <br><br>"
                 "<b> Brew flow will not resume.</b><br><br>"

            )
            self.brewinterruptbeginbutton.setText("Continue")
            self.brewinterruptbeginbutton.clicked.disconnect()
            self.brewinterruptbeginbutton.clicked.connect(self.BrewInterrupt)

        if self.brewinterrupt_passed[1] or self.brewinterrupt_failed[1]:
            print("Update Brew Interrupt Step")
            self.brewinterruptlabel.setText(
                " <b>  Each heater should draw approximately 8±1 amps</b> <br><br>"
                " <i>  Please enter the amperage of Phase A as displayed by the phase readings window </i><br><br>"
            )
            self.brewinterruptbeginbutton.setText("Continue")
            self.brewinterruptbeginbutton.clicked.disconnect()
            self.brewinterruptbeginbutton.clicked.connect(self.BrewInterrupt)


        if self.brewinterrupt_completed == True:
            self.brewinterruptlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Brew Interrupt test has been completed successfully!</b><br><br>"
            )
            self.brewinterruptbeginbutton.setText("Results")
            self.brewinterruptbeginbutton.clicked.disconnect()
            self.brewinterruptbeginbutton.clicked.connect(self.BrewInterruptResults)

            self.brewinterruptrestart = QPushButton("Restart", self)
            self.brewinterruptrestart.clicked.connect(self.BrewInterruptRestart)
            self.brewinterruptrestart.setFixedWidth(200)
            self.brewinterrupttestbuttonlayout.addWidget(self.brewinterruptrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetBrewInterruptResults(self):
        return self.brewinterrupt_results

    def BrewInterruptTestPath(self, path):
        self.test_path = path

    def insert_brewinterrupt_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Brew Interrupt Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Brew Interrupt section not found.")
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

    def BrewInterruptRestart(self):
        print("Restarting Brew Interrupt Test")

    def BrewInterruptResults(self):
        print("Printing Brew Interrupt Test Results")