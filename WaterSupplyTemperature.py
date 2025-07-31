from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- WaterTemp Check

class WaterTempTest(QWidget):

    def __init__(self):
        super().__init__()

        self.watertemp_results = ""
        self.watertemp_passed = [False, False, False]
        self.watertemp_failed = [False, False, False]
        self.watertemp_completed = False
        self.current_watertemp_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.watersupplylabellayout = QHBoxLayout()
        self.watertemptestbuttonlayout = QHBoxLayout()

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

        self.watertemplabel = QLabel(
            "<b>1. If water supply is connected to the Beverage Maker, "
                "disconnect water supply from the Beverage Maker. <br><br>"
                "Open V9 for 10 seconds to flow water through TM2. <br><br>"
                "2. Measure the temperature of the water from the water "
                "supply by reading thermometer TM2. </b><br><br>"
            "<i> The temperature of the water should be 62° F (17° C) to 72° F (22° C). </i><br><br>"
        )

        self.watertemplabel.setTextFormat(Qt.TextFormat.RichText)
        self.watertemplabel.setWordWrap(True)
        self.watertemplabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.watertemplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.watertemplabel)

        self.watersupplylabellayout.addWidget(scroll)
        layout.addLayout(self.watersupplylabellayout)
        layout.addLayout(self.watertemptestbuttonlayout)
        try:
            self.watertempbeginbutton = QPushButton("Begin")
            self.watertempbeginbutton.setFixedWidth(200)
            self.watertempbeginbutton.clicked.connect(self.WaterTemp)
            self.watertemptestbuttonlayout.addWidget(self.watertempbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(watertemp, f"WaterTemp")

    def WaterTemp(self):
        try:
            # STEP 1 — 4.5 mΩ
            if self.current_watertemp_step == 0:
                value, ok = QInputDialog.getDouble(
                    self,
                    "Check Temperature",
                    "Please enter the temperature displayed on provided thermometer:",
                    decimals=1,
                    min=0.0,
                    max=300.0,
                    step=0.01
                )

                if ok:
                    if value < 60:
                        tempsystem = "C"
                    else:
                        tempsystem = "F"
                    result_line = f"Water Supply Temperature Test {self.current_watertemp_step + 1}: {value}°{tempsystem} "
                    if tempsystem == "F":
                        if value >= 62 and value <=72:
                            result_line += "\tPASS"
                        else:
                            result_line += "\tFAIL"
                    elif tempsystem == "C":
                        if value >= 17 and value <=22:
                            result_line += "\tPASS"
                        else:
                            result_line += "\tFAIL"
                    self.insert_watertemp_result(result_line)
                    print(f"User entered: {value} mA")
                    self.watertemp_results += f"Test {self.current_watertemp_step + 1} Result: {value} mA\n"
                    self.watertemp_passed[0] = True
                    self.watertemp_failed[0] = False
                    self.current_watertemp_step += 1
                    self.updateWaterTempStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateWaterTempStep(self):
        if self.watertemp_passed[0] or self.watertemp_failed[0]:
            self.watertemplabel.setText(
                "<b>Test Complete.</b><br><br>"
                "<b>The Water Supply Temperature test has been completed successfully.</b><br><br>"
            )

            self.watertempbeginbutton.setText("Results")
            self.watertempbeginbutton.clicked.disconnect()
            self.watertempbeginbutton.clicked.connect(self.WaterTempResults)

            self.watertemprestart = QPushButton("Restart", self)
            self.watertemprestart.clicked.connect(self.WaterTempRestart)
            self.watertemprestart.setFixedWidth(200)
            self.watertemptestbuttonlayout.addWidget(self.watertemprestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetWaterTempResults(self):
        return self.watertemp_results

    def WaterTempTestPath(self, path):
        self.test_path = path

    def insert_watertemp_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Water Supply Temperature Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Water Supply Temperature section not found.")
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

    def WaterTempRestart(self):
        print("Restarting WaterTemp Test")

    def WaterTempResults(self):
        print("Printing WaterTemp Test Results")
