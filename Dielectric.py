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


#-------------------------------------------------------- Dielectric Test
class DielectricTest(QWidget):


        def __init__(self):
                super().__init__()

                #temp self.phase
                self.phase1read = 0
                self.phase2read = 0
                self.phase3read = 0

                self.dielectric_results = ""

                self.dielectric_passed = [False, False]
                self.dielectric_failed = [False, False]
                self.dielectric_completed = False
                self.current_dielectric_step = 0

                layout = QVBoxLayout()
                spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                layout.addSpacerItem(spacer)

                layout.addStretch(1)
                
                dielectric_results = "Some test results."

                self.dielectriclabellayout = QHBoxLayout()

                self.dielectrictestbuttonlayout = QHBoxLayout()


                self.scroll = QScrollArea()
                self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


                self.scroll.setStyleSheet("""
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

                self.scroll.setMinimumHeight(500)
                self.scroll.setMaximumWidth(1200)
                self.scroll.setWidgetResizable(True)

                self.dielectriclabel = QLabel("""
                Begin by removing side panel<br><br><br>
                <b>1. Disconnect the P1 connector from J1 connector on circuit board.</b><br<br>
                <b>2. Install IAS11003B circular box connector into power input.</b><br><br>
                <i>Confirm test box leads are connected to hipot tester.</i><br><br>
                <b>2a. Install red and black test box jumpers from C to H.<br><br>
                Turn on the QuadTech Guardian 2510 Hipot Tester and press start.<br><br>
                The tester will increase the voltage of the Hi Pot test set in increments of 250 to 500 volts per second<br>
                until 1500 volts are applied across test connection and maintain the voltage at the 1500 volt level for 60 seconds.</b><br><br>
                Press Begin to continue.<br><br>
                """)

                self.dielectriclabel.setTextFormat(Qt.TextFormat.RichText)
                self.dielectriclabel.setWordWrap(True)
                self.dielectriclabel.setStyleSheet("""
                        font-size: 18px;
                        padding-top: 50px;
                        padding-left: 50px;
                        padding-right: 50px;
                        padding-bottom: 50px;
                        """)
                self.dielectriclabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.scroll.setWidget(self.dielectriclabel)


                self.dielectriclabellayout.addWidget(self.scroll)
                layout.addLayout(self.dielectriclabellayout)
                layout.addLayout(self.dielectrictestbuttonlayout)

                try:
                        self.dielectricbeginbutton = QPushButton("Begin", self)
                        self.dielectricbeginbutton.setFixedWidth(200)
                        self.dielectricbeginbutton.clicked.connect(self.Dielectric)
                        self.dielectrictestbuttonlayout.addWidget(self.dielectricbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

                except Exception as e:
                        print(f"Error while opening workorder: {e}")

                #-------------------------------------------------------------------- Phase Readings


                self.phaselayout = QHBoxLayout()
                #self.phaselayout.setContentsMargins(0, 100, 0, 0)

                spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                layout.addSpacerItem(spacer1)

                spacer2 = QSpacerItem(720, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
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

                self.setLayout(layout)

        @pyqtSlot(float)
        def show_current1(self, amps):
                self.phase1.setText(f"Phase 1: {amps:.3f} A")

        @pyqtSlot(float)
        def show_current2(self, amps):
                self.phase2.setText(f"Phase 2: {amps:.3f} A")

        @pyqtSlot(float)
        def show_current3(self, amps):
                self.phase3.setText(f"Phase 3: {amps:.3f} A")

        def Dielectric(self):
                try:
                                        # STEP 1 — 4.5 mΩ
                        if self.current_dielectric_step == 0:
                                value, ok = QInputDialog.getDouble(
                                        self,
                                        "Check Hi Pot Current",
                                        "Please enter the maximum current measured in milliamperes during the test period:",
                                        decimals=3,
                                        min=0.0,
                                        max=100.0,
                                        step=0.01
                                )

                                if ok:
                                        result_line = f"Hi Pot Current Test {self.current_dielectric_step + 1}: {value} mA"
                                        if value <= 2:
                                                result_line += "\tPASS"
                                        else:
                                                result_line += "\tFAIL"
                                        self.insert_dielectric_result(result_line)
                                        print(f"User entered: {value} mA")
                                        self.dielectric_results += f"Test {self.current_dielectric_step + 1} Result: {value} mA\n"
                                        self.dielectric_passed[0] = True
                                        self.dielectric_failed[0] = False
                                        self.current_dielectric_step += 1
                                        self.updateDielectricStep()



                        elif self.current_dielectric_step == 1:
                                value, ok = QInputDialog.getDouble(
                                        self,
                                        "Check Megaohmmeter",
                                        "Please enter the resistance measured in megaohms:",
                                        decimals=3,
                                        min=0.0,
                                        max=100.0,
                                        step=0.01
                                )

                                if ok:
                                        result_line = f"Megaohmmeter Resistance Test {self.current_dielectric_step + 1}: {value} mΩ"
                                        if value >= 2:
                                                result_line += "\tPASS"
                                        else:
                                                result_line += "\tFAIL"
                                        self.insert_dielectric_result(result_line)
                                        print(f"User entered: {value} mΩ")
                                        self.dielectric_results += f"Test {self.current_dielectric_step + 1} Result: {value} mΩ\n"
                                        self.dielectric_passed[1] = True
                                        self.dielectric_failed[1] = False
                                        self.updateDielectricStep()


                        elif self.dielectric_completed:
                                msg1 = QMessageBox()
                                msg1.setWindowTitle("Test Completed!")
                                msg1.setText("The dielectric test has been completed successfully.")
                                #msg1.setIcon(QMessageBox.Icon.Information)

                                pass_button = msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)

                                msg1.exec()

                except Exception as e:
                        print(f"Error in: {e}")


        def updateDielectricStep(self):
                if self.dielectric_passed[0] or self.dielectric_failed[0]:
                        self.dielectriclabel.setText(
                                "<b>3. Connect QuadTech megohmmeter by connecting C and M jumpers on the test box.<br><br>"
                                "Set scale on megohmmeter to 500 volts and 100M.<br><br>"
                                "Turn megohmmeter power on.<br><br>"
                                "Flip switch to charge and then to measure.</b><br><br>"
                                "<i>The megohmmeter gauge must be greater than 2.</i><br><br>")

                        self.dielectricbeginbutton.setText("Continue")
                        self.dielectricbeginbutton.clicked.disconnect()
                        self.dielectricbeginbutton.clicked.connect(self.Dielectric)

                if self.dielectric_passed[1] or self.dielectric_failed[1]:
                        self.dielectriclabel.setText(
                                "<b>Test Complete.<br><br>"
                                "The Dielectric Test has been completed successfully!<br><br>"
                                "Please flip the megohmmeter switch to discharge and then power off.<br><br>"
                                "Disconnect IAS11003B circular box connector from the coffee maker.<br><br>"
                                "Reconnect P1 connector to J1 connector on circuit board.</b><br><br>")

                        self.dielectricbeginbutton.setText("Results")
                        self.dielectricbeginbutton.clicked.disconnect()
                        self.dielectricbeginbutton.clicked.connect(self.DielectricResults)

                        self.dielectricrestart = QPushButton("Restart", self)
                        self.dielectricrestart.clicked.connect(self.DielectricRestart)
                        self.dielectricrestart.setFixedWidth(200)
                        self.dielectrictestbuttonlayout.addWidget(self.dielectricrestart,
                                                                  alignment=Qt.AlignmentFlag.AlignCenter)

        def GetDielectricResults(self):
                return self.dielectric_results

        def DielectricTestPath(self, path):
                self.test_path = path

        def insert_dielectric_result(self, result_line: str):
                try:
                        with open(self.test_path, "r", encoding="utf-8") as file:
                                lines = file.readlines()

                        header_index = -1
                        found_line_index = -1
                        test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

                        # Step 1: Find the Resistance Test section
                        for i, line in enumerate(lines):
                                if line.strip() == ">>Dielectric Test<<":
                                        header_index = i
                                        break

                        if header_index == -1:
                                print("Dielectric section not found.")
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

        def DielectricRestart(self):
                print("Restarting Dielectric Test")

        def DielectricResults(self):
                print("Printing Dielectric Test Results")
