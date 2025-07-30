from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- AmbientTemperature Check

class AmbientTemperatureTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1200, 600)


        self.ambienttemp_passed = [False, False, False]
        self.ambienttemp_failed = [False, False, False]
        self.ambienttemp_completed = False
        self.current_ambienttemp_step = 0

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
        #tabs.addTab(ambienttemp, f"AmbientTemperature")

    def AmbientTemperature(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_ambienttemp_step == 0:
                msg1.setWindowTitle("Ambient Temperature Test")
                msg1.setText( "<i>The ambient temperature is between 70° F (21° C) and 85° F (29° C).</i><br><br>")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.ambienttemp_passed[0] = True
                    self.ambienttemp_failed[0] = False
                    self.updateAmbientTemperatureStep()
                    self.current_ambienttemp_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.ambienttemp_passed[0] = False
                    self.ambienttemp_failed[0] = True
                    self.updateAmbientTemperatureStep()
                    self.current_ambienttemp_step += 1


        except Exception as e:
            print(f"Error: {e}")

    def updateAmbientTemperatureStep(self):


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

    def AmbientTemperatureRestart(self):
        print("Restarting AmbientTemperature Test")

    def AmbientTemperatureResults(self):
        print("Printing AmbientTemperature Test Results")