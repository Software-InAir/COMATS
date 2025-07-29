from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
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


        self.watertemp_passed = [False, False, False]
        self.watertemp_failed = [False, False, False]
        self.watertemp_completed = False
        self.current_watertemp_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

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
        layout.addWidget(scroll)
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
            msg1 = QMessageBox()
            msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_watertemp_step == 0:
                msg1.setWindowTitle("Check WaterTemp")
                msg1.setText("The water temperature should be at or between 62° F (17° C) to 72° F (22° C). ")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.watertemp_passed[0] = True
                    self.watertemp_failed[0] = False
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.watertemp_passed[0] = False
                    self.watertemp_failed[0] = True
                    self.updateWaterTempStep()
                    self.current_watertemp_step += 1

            # Completed
            elif self.current_watertemp_step == 1:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Water Supply Temperature test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateWaterTempStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateWaterTempStep(self):
        if self.watertemp_passed[0] or self.watertemp_failed[0]:
            self.watertemplabel.setText(
                "<b>Water Supply Temperature Test Completed!</b><br><br>"
            )

            self.watertempbeginbutton.setText("Results")
            self.watertempbeginbutton.clicked.disconnect()
            self.watertempbeginbutton.clicked.connect(self.WaterTempResults)

            self.watertemprestart = QPushButton("Restart", self)
            self.watertemprestart.clicked.connect(self.WaterTempRestart)
            self.watertemprestart.setFixedWidth(200)
            self.watertemptestbuttonlayout.addWidget(self.watertemprestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def WaterTempRestart(self):
        print("Restarting WaterTemp Test")

    def WaterTempResults(self):
        print("Printing WaterTemp Test Results")
