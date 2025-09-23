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



#------------------------------------------------------- HotWaterLight Check

class HotWaterLightTest(QWidget):

    def __init__(self):
        super().__init__()

        self.hotwaterlight_results = ""
        self.hotwaterlight_passed = [False, False, False, False]
        self.hotwaterlight_failed = [False, False, False, False]
        self.hotwaterlight_completed = False
        self.current_hotwaterlight_step = 0

        # -------- temp self.phase
        self.phase1read = 0
        self.phase2read = 0
        self.phase3read = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.hotwaterlightlabellayout = QHBoxLayout()
        self.hotwaterlighttestbuttonlayout = QHBoxLayout()

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

        self.hotwaterlightlabel = QLabel(
            "<i> Once water is hot (approximately two minutes) the HOT WATER light should <br><br>"
            "   come on while heaters should turn off (indicated by current drop) as shown by the self.phase readings window.</i>"
        )

        self.hotwaterlightlabel.setTextFormat(Qt.TextFormat.RichText)
        self.hotwaterlightlabel.setWordWrap(True)
        self.hotwaterlightlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.hotwaterlightlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.hotwaterlightlabel)


        self.hotwaterlightlabellayout.addWidget(scroll)
        layout.addLayout(self.hotwaterlightlabellayout)
        layout.addLayout(self.hotwaterlighttestbuttonlayout)
        try:
            self.hotwaterlightbeginbutton = QPushButton("Begin")
            self.hotwaterlightbeginbutton.setFixedWidth(200)
            self.hotwaterlightbeginbutton.clicked.connect(self.HotWaterLight)
            self.hotwaterlighttestbuttonlayout.addWidget(self.hotwaterlightbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(hotwaterlight, f"HotWaterLight")

    @pyqtSlot(float)
    def show_current1(self, amps):
        self.phase1.setText(f"Phase 1: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current2(self, amps):
        self.phase2.setText(f"Phase 2: {amps:.3f} A")

    @pyqtSlot(float)
    def show_current3(self, amps):
        self.phase3.setText(f"Phase 3: {amps:.3f} A")

    def HotWaterLight(self):
        try:
            msg1 = QMessageBox()

            if self.current_hotwaterlight_step == 0:
                msg1.setWindowTitle("Hot Water Indicator Light")
                msg1.setText("The Hot Water Indicator Light has been activated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    result_line = f"Hot Water Light Test: "
                    result_line += "\tPASS"
                    self.insert_hotwaterlight_result(result_line)
                    self.hotwaterlight_passed[0] = True
                    self.hotwaterlight_failed[0] = False
                    self.hotwaterlight_completed = True
                    self.updateHotWaterLightStep()
                    self.current_hotwaterlight_step += 1
                elif msg1.clickedButton() == fail_button:
                    result_line = f"Hot Water Light Test: "
                    result_line += "\tFAIL"
                    self.insert_hotwaterlight_result(result_line)
                    self.hotwaterlight_passed[0] = False
                    self.hotwaterlight_failed[0] = True
                    self.hotwaterlight_completed = True
                    self.updateHotWaterLightStep()




            # Completed
            elif self.hotwaterlight_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The HotWaterLight test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateHotWaterLightStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHotWaterLightStep(self):

        if self.hotwaterlight_passed[0] or self.hotwaterlight_failed[0]:
            print("Update Hot Water Light Step")
            self.hotwaterlightlabel.setText(
                "  <i> The LOW WATER lamp should turn off once tank is full. </i><br><br>"

            )
            self.hotwaterlightbeginbutton.setText("Continue")
            self.hotwaterlightbeginbutton.clicked.disconnect()
            self.hotwaterlightbeginbutton.clicked.connect(self.HotWaterLight)

        if self.hotwaterlight_passed[1] or self.hotwaterlight_failed[1]:
            print("Update Hot Water Light Step")
            self.hotwaterlightlabel.setText(
                " <b>  Each heater should draw approximately 8±1 amps</b> <br><br>"
                " <i>  Please enter the amperage of Phase A as displayed by the self.phase readings window </i><br><br>"
            )
            self.hotwaterlightbeginbutton.setText("Continue")
            self.hotwaterlightbeginbutton.clicked.disconnect()
            self.hotwaterlightbeginbutton.clicked.connect(self.HotWaterLight)


        if self.hotwaterlight_completed == True:
            self.hotwaterlightlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Hot Water Light test has been completed successfully!</b><br><br>"
            )
            self.hotwaterlightbeginbutton.setText("Results")
            self.hotwaterlightbeginbutton.clicked.disconnect()
            self.hotwaterlightbeginbutton.clicked.connect(self.HotWaterLightResults)

            self.hotwaterlightrestart = QPushButton("Restart", self)
            self.hotwaterlightrestart.clicked.connect(self.HotWaterLightRestart)
            self.hotwaterlightrestart.setFixedWidth(200)
            self.hotwaterlighttestbuttonlayout.addWidget(self.hotwaterlightrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def GetHotWaterLightResults(self):
        return self.hotwaterlight_results

    def HotWaterLightTestPath(self, path):
        self.test_path = path

    def insert_hotwaterlight_result(self, result_line: str):
        try:
            with open(self.test_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            header_index = -1
            found_line_index = -1
            test_id = result_line.split(":")[0].strip()  # e.g., "Resistance Test 2"

            # Step 1: Find the Resistance Test section
            for i, line in enumerate(lines):
                if line.strip() == ">>Hot Water Light Test<<":
                    header_index = i
                    break

            if header_index == -1:
                print("Hot Water Light section not found.")
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

    def HotWaterLightRestart(self):
        print("Restarting HotWaterLight Test")

    def HotWaterLightResults(self):
        print("Printing HotWaterLight Test Results")