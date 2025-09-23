from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox, QInputDialog
)

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot

from InstrumentWorker import InstrumentWorker





class Worker(QObject):
    finished = pyqtSignal()
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)



#------------------------------------------------------- AmbientTemperature Check

class AmbientTemperatureTest(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(1200, 600)

        self.ambienttemp_results = ""
        self.ambienttemp_passed = [False, False, False]
        self.ambienttemp_failed = [False, False, False]
        self.ambienttemp_completed = False
        self.current_ambienttemp_step = 0

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.ambientlabellayout = QHBoxLayout()

        ambienttemptestbuttonlayout = QHBoxLayout()

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

        self.ambienttemplabel = QLabel(
            "<b>1. Using the wall thermometer, measure the temperature in the adjacent"
            " area of the test environment. </b><br><br>"
            "<i>The temperature should be between 70° F (21° C) and 85° F (29° C).</i><br><br>"
        )

        self.ambienttemplabel.setTextFormat(Qt.TextFormat.RichText)
        self.ambienttemplabel.setWordWrap(True)
        self.ambienttemplabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.ambienttemplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.ambienttemplabel)

        self.ambientlabellayout.addWidget(scroll)
        layout.addLayout(self.ambientlabellayout)
        layout.addLayout(ambienttemptestbuttonlayout)
        try:
            self.ambienttempbeginbutton = QPushButton("Begin")
            self.ambienttempbeginbutton.setFixedWidth(200)
            self.ambienttempbeginbutton.clicked.connect(self.AmbientTemperature)
            ambienttemptestbuttonlayout.addWidget(self.ambienttempbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(ambienttemp, f"AmbientTemperature")

    @pyqtSlot(float)
    def show_current1(self, amps):
        self.phase1.setText(f"Phase 1: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current2(self, amps):
        self.phase2.setText(f"Phase 2: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current3(self, amps):
        self.phase3.setText(f"Phase 3: {amps:.3f} A")

    def AmbientTemperature(self):
        try:
            # STEP 1 — 4.5 mΩ
            if self.current_ambienttemp_step == 0:
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
                        tempsystem = "°C"
                    else:
                        tempsystem = "°F"
                    result_line = f"Ambient Temperature Test {self.current_ambienttemp_step + 1}: {value}{tempsystem} "
                    if tempsystem == "°F":
                        if value >= 70 and value <=85:
                            result_line += "\tPASS"
                        else:
                            result_line += "\tFAIL"
                    elif tempsystem == "°C":
                        if value >= 21 and value <=29:
                            result_line += "\tPASS"
                        else:
                            result_line += "\tFAIL"
                    self.insert_ambienttemp_result(result_line)
                    print(f"User entered: {value} mA")
                    self.ambienttemp_results += f"Test {self.current_ambienttemp_step + 1} Result: {value}\n"
                    self.ambienttemp_passed[0] = True
                    self.ambienttemp_failed[0] = False
                    self.current_ambienttemp_step += 1
                    self.updateAmbientTempStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateAmbientTempStep(self):


        if self.ambienttemp_passed[0] or self.ambienttemp_failed[0]:
            self.ambienttemplabel.setText(
                "<b>Test Complete.</b><br><br>"
                "<b>The Ambient Temperature Test has been completed successfully!<br><br>"
            )
            self.ambienttempbeginbutton.setText("Results")
            self.ambienttempbeginbutton.clicked.disconnect()
            self.ambienttempbeginbutton.clicked.connect(self.AmbientTemperatureResults)

            self.ambienttemprestart = QPushButton("Restart", self)
            self.ambienttemprestart.clicked.connect(self.AmbientTemperatureRestart)
            self.ambienttemprestart.setFixedWidth(200)
            self.ambienttemptestbuttonlayout.addWidget(self.ambienttemprestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetAmbientTempResults(self):
        return self.ambienttemp_results

    def AmbientTempTestPath(self, path):
        self.test_path = path

    def insert_ambienttemp_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Ambient Temperature Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Ambient Temperature section not found.")
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

    def AmbientTemperatureRestart(self):
        print("Restarting AmbientTemperature Test")

    def AmbientTemperatureResults(self):
        print("Printing AmbientTemperature Test Results")