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



#------------------------------------------------------- Temperature Check

class TemperatureTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker, parent=None):
        super().__init__()

        self.instrument = instrument_worker

        self.temperature_results = ""
        self.temperature_passed = [False, False, False, False]
        self.temperature_failed = [False, False, False, False]
        self.temperature_completed = False
        self.current_temperature_step = 0

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.temperaturelabellayout = QHBoxLayout()
        self.temperaturetestbuttonlayout = QHBoxLayout()

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

        self.temperaturelabel = QLabel(
            "<b><i> PERFORM AT LEAST THREE BREW CYCLES BEFORE TAKING TEMPERATURE AND TIMING MEASUREMENTS. </i><br><br>"
            "Measure the brew cup peak temperature using the temperature test brew cup IAS2405001 </b> <br><br>"
            "<i>Temperature for PN 11225-31 should be 193°±3° F. <br><br>"
            "All other units should have a measured temperature of 188°±3° F. </i><br><br>"



        )

        self.temperaturelabel.setTextFormat(Qt.TextFormat.RichText)
        self.temperaturelabel.setWordWrap(True)
        self.temperaturelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.temperaturelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.temperaturelabel)


        self.temperaturelabellayout.addWidget(scroll)
        layout.addLayout(self.temperaturelabellayout)
        layout.addLayout(self.temperaturetestbuttonlayout)
        try:
            self.temperaturebeginbutton = QPushButton("Begin")
            self.temperaturebeginbutton.setFixedWidth(200)
            self.temperaturebeginbutton.clicked.connect(self.Temperature)
            self.temperaturetestbuttonlayout.addWidget(self.temperaturebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(temperature, f"Temperature")

    @pyqtSlot(float)
    def show_current1(self, amps):
        self.phase1.setText(f"Phase 1: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current2(self, amps):
        self.phase2.setText(f"Phase 2: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current3(self, amps):
        self.phase3.setText(f"Phase 3: {amps:.3f} A")

    def Temperature(self):
        try:

                msg1 = QMessageBox()
                # msg1.setIcon(QMessageBox.Icon.Information)

                if self.current_temperature_step == 0:
                    value1, ok = QInputDialog.getDouble(
                        self,
                        "Brew Cup Temperature",
                        "Please enter the temperature displayed by temperature test brew cup IAS2405001 ",
                        decimals=2,
                        min=0.0,
                        max=300.0,
                        step=.01
                    )
                    self.temperature_results += f""
                    if ok:
                        result_line = f"Brew Cup Temperature: {value1}°F \n"
                        if value1 >= 185 and value1 <= 191:
                            result_line += "\tPASS"
                            self.temperature_passed[0] = True
                            self.temperature_failed[0] = False
                        else:
                            result_line += "\tFAIL"
                            self.temperature_passed[0] = False
                            self.temperature_failed[0] = True
                        self.insert_temperature_result(result_line)
                        self.current_temperature_step += 1
                        self.updateTemperatureStep()


                elif self.current_temperature_step == 1:
                    value1, ok = QInputDialog.getDouble(
                        self,
                        "Server Temperature",
                        "Please enter the temperature of the server as displayed by provided handheld thermometer.",
                        value=0.00,
                        decimals=2,
                        min=0.00,
                        max=300.00,
                        step=.01
                    )
                    self.temperature_results += f""
                    if ok:
                        result_line = f"Server Temperature: {value1}°F\n"
                        if value1 >= 165 and value1 <= 185:
                            result_line += "\tPASS"
                            self.temperature_passed[1] = True
                            self.temperature_failed[1] = False
                        else:
                            result_line += "\tFAIL"
                            self.temperature_passed[1] = False
                            self.temperature_failed[1] = True
                        self.insert_temperature_result(result_line)
                        self.current_temperature_step += 1
                        self.temperature_completed = True
                        self.updateTemperatureStep()


                # Completed
                elif self.temperature_completed:
                    msg1.setWindowTitle("Test Completed!")
                    msg1.setText("The Temperature test has been completed successfully.")
                    msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                    msg1.exec()

                    self.updateTemperatureStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateTemperatureStep(self):

        if self.temperature_passed[0] or self.temperature_failed[0]:
            print("Update Temperature Step")
            self.temperaturelabel.setText(
                "<b>Measure the server temperature after a brew cycle using the hand held digital thermometer. </b><br><br>"
                "<i>Server temperature should be 175°±10° F for all units. </i><br><br>"
            )
            self.temperaturebeginbutton.setText("Continue")
            self.temperaturebeginbutton.clicked.disconnect()
            self.temperaturebeginbutton.clicked.connect(self.Temperature)


        if self.temperature_completed == True:
            self.temperaturelabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Temperature test has been completed successfully!</b><br><br>"
            )
            self.temperaturebeginbutton.setText("Results")
            self.temperaturebeginbutton.clicked.disconnect()
            self.temperaturebeginbutton.clicked.connect(self.TemperatureResults)

            self.temperaturerestart = QPushButton("Restart", self)
            self.temperaturerestart.clicked.connect(self.TemperatureRestart)
            self.temperaturerestart.setFixedWidth(200)
            self.temperaturetestbuttonlayout.addWidget(self.temperaturerestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetTemperatureResults(self):
        return self.temperature_results

    def TemperatureTestPath(self, path):
        self.test_path = path

    def insert_temperature_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Temperature Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Temperature section not found.")
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

    def TemperatureRestart(self):
        print("Restarting Temperature Test")

    def TemperatureResults(self):
        print("Printing Temperature Test Results")