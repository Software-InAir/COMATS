from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- HeatedWater Check

class HeatedWaterTest(QWidget):

    def __init__(self):
        super().__init__()

        self.heatedwater_results = ""
        self.heatedwater_passed = [False, False, False, False]
        self.heatedwater_failed = [False, False, False, False]
        self.heatedwater_completed = False
        self.current_heatedwater_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.heatedwaterlabellayout = QHBoxLayout()
        self.heatedwatertestbuttonlayout = QHBoxLayout()

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

        self.heatedwaterlabel = QLabel(
            "<b> Place server under faucet. <br><br>"
            "   Push the HOT WATER button and verify that heated water comes out of the faucet. </b> <br><br>"
            "<i> Verify flow rate is greater than 0.23 gallons per minute as indicated by FM. </i>"

        )

        self.heatedwaterlabel.setTextFormat(Qt.TextFormat.RichText)
        self.heatedwaterlabel.setWordWrap(True)
        self.heatedwaterlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.heatedwaterlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.heatedwaterlabel)


        self.heatedwaterlabellayout.addWidget(scroll)
        layout.addLayout(self.heatedwaterlabellayout)
        layout.addLayout(self.heatedwatertestbuttonlayout)
        try:
            self.heatedwaterbeginbutton = QPushButton("Begin")
            self.heatedwaterbeginbutton.setFixedWidth(200)
            self.heatedwaterbeginbutton.clicked.connect(self.HeatedWater)
            self.heatedwatertestbuttonlayout.addWidget(self.heatedwaterbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(heatedwater, f"HeatedWater")

    def HeatedWater(self):
        try:

                msg1 = QMessageBox()
                # msg1.setIcon(QMessageBox.Icon.Information)

                if self.current_heatedwater_step == 0:
                    value1, ok = QInputDialog.getDouble(
                        self,
                        "Flow Rate Measurement",
                        "Please enter the flow rate as indicated by FM ",
                        decimals=2,
                        min=0.0,
                        max=200.0,
                        step=.01
                    )
                    self.heatedwater_results += f""
                    if ok:
                        result_line = f"Heated Water Flow Rate: {value1}GPM \n"
                        if value1 >= 0.23:
                            result_line += "\tPASS"
                            self.heatedwater_passed[0] = True
                            self.heatedwater_failed[0] = False
                        else:
                            result_line += "\tFAIL"
                            self.heatedwater_passed[0] = False
                            self.heatedwater_failed[0] = True
                        self.insert_heatedwater_result(result_line)
                        self.current_heatedwater_step += 1
                        self.heatedwater_completed = True
                        self.updateHeatedWaterStep()



                # Completed
                elif self.heatedwater_completed:
                    msg1.setWindowTitle("Test Completed!")
                    msg1.setText("The HeatedWater test has been completed successfully.")
                    msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                    msg1.exec()

                    self.updateHeatedWaterStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHeatedWaterStep(self):


        if self.heatedwater_completed == True:
            self.heatedwaterlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Heated Water test has been completed successfully!</b><br><br>"
            )
            self.heatedwaterbeginbutton.setText("Results")
            self.heatedwaterbeginbutton.clicked.disconnect()
            self.heatedwaterbeginbutton.clicked.connect(self.HeatedWaterResults)

            self.heatedwaterrestart = QPushButton("Restart", self)
            self.heatedwaterrestart.clicked.connect(self.HeatedWaterRestart)
            self.heatedwaterrestart.setFixedWidth(200)
            self.heatedwatertestbuttonlayout.addWidget(self.heatedwaterrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetHeatedWaterResults(self):
        return self.heatedwater_results

    def HeatedWaterTestPath(self, path):
        self.test_path = path

    def insert_heatedwater_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Heated Water Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Heated Water section not found.")
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

    def HeatedWaterRestart(self):
        print("Restarting HeatedWater Test")

    def HeatedWaterResults(self):
        print("Printing HeatedWater Test Results")