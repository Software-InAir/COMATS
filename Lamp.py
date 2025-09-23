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



#------------------------------------------------------- Lamp Check

class LampTest(QWidget):

    def __init__(self, instrument_worker: InstrumentWorker, parent=None):
        super().__init__()

        self.instrument = instrument_worker

        self.lamp_results = ""
        self.lamp_passed = [False, False, False]
        self.lamp_failed = [False, False, False]
        self.lamp_completed = False
        self.current_lamp_step = 0

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        #spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #layout.addSpacerItem(spacer)

        self.lamplabellayout = QHBoxLayout()
        self.lamptestbuttonlayout = QHBoxLayout()

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

        self.lamplabel = QLabel(
            "<b> Push the TEST/LOW WATER button and verify that all five lamps are illuminated.</b> <br><br>" 
            "<i> All five indicator lights should be illuminated. </i> <br><br>"
        )

        self.lamplabel.setTextFormat(Qt.TextFormat.RichText)
        self.lamplabel.setWordWrap(True)
        self.lamplabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.lamplabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.lamplabel)


        self.lamplabellayout.addWidget(scroll)
        layout.addLayout(self.lamplabellayout)
        layout.addLayout(self.lamptestbuttonlayout)
        try:
            self.lampbeginbutton = QPushButton("Begin")
            self.lampbeginbutton.setFixedWidth(200)
            self.lampbeginbutton.clicked.connect(self.Lamp)
            self.lamptestbuttonlayout.addWidget(self.lampbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(lamp, f"Lamp")

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

    def Lamp(self):
        try:

            msg1 = QMessageBox()
            # msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_lamp_step == 0:
                msg1.setWindowTitle("Illuminated Indicators")
                msg1.setText("All five indicators illuminated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Lamp Test: "
                    result_line += "\tPASS"
                    self.insert_lamp_result(result_line)
                    self.lamp_passed[0] = True
                    self.lamp_failed[0] = False
                    self.lamp_completed = True
                    self.updateLampStep()
                    self.current_lamp_step += 1
                    self.lamp_completed = True
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Lamp Test: "
                    result_line += "\tFAIL"
                    self.insert_lamp_result(result_line)
                    self.lamp_passed[0] = False
                    self.lamp_failed[0] = True
                    self.updateLampStep()
                    self.current_lamp_step += 1
                    self.lamp_completed = True
            # Completed
            elif self.lamp_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Lamp test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateLampStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateLampStep(self):

        if self.lamp_completed:
            self.lamplabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Lamp test has been completed successfully!</b><br><br>"
            )
            self.lampbeginbutton.setText("Results")
            self.lampbeginbutton.clicked.disconnect()
            self.lampbeginbutton.clicked.connect(self.LampResults)

            self.lamprestart = QPushButton("Restart", self)
            self.lamprestart.clicked.connect(self.LampRestart)
            self.lamprestart.setFixedWidth(200)
            self.lamptestbuttonlayout.addWidget(self.lamprestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetLampResults(self):
        return self.lamp_results

    def LampTestPath(self, path):
        self.test_path = path

    def insert_lamp_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Lamp Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Lamp section not found.")
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

    def LampRestart(self):
        print("Restarting Lamp Test")

    def LampResults(self):
        print("Printing Lamp Test Results")