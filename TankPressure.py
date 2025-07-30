from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- TankPressure Check

class TankPressureTest(QWidget):
    tankpressure_results = "Some Tank Pressure Results!"
    def __init__(self):
        super().__init__()


        self.tankpressure_passed = [False, False, False]
        self.tankpressure_failed = [False, False, False]
        self.tankpressure_completed = False
        self.current_tankpressure_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.tankpressurelabellayout = QHBoxLayout()
        self.tankpressuretestbuttonlayout = QHBoxLayout()

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

        self.tankpressurelabel = QLabel(
            "<b>Remove plastic drain tube from clip behind server.<br><br>"
            "Use 11/16 wrench to remove pressure relief valve.<br><br>"
            "Use a 7/16 wrench to secure 1/8 inch NPT plug wrapped with teflon tape.<br><br>"
            "1. Replace the pressure relief valve with a 1/8 inch NPT plug prior to " 
            "testing.<br><br>"
            "Close V10 then turn V8 vertical. <br><br>"
            "2. Connect the Beverage Maker to water supply and then open V10.<br><br>"
            "3. Let tank fill with water. Flow meter will go to zero when tank is full.<br><br>" 
            "4. Adjust water pressure by rotating V7 clockwise until PG2 reads 130 psig (8.96 barg).<br><br>"
            "Hold for a minimum of 5 minutes.<br><br>"
            "Inspect tank for leaks.<br><br>"
            "<i>No leaks are allowed.</i><br><br>"
        )

        self.tankpressurelabel.setTextFormat(Qt.TextFormat.RichText)
        self.tankpressurelabel.setWordWrap(True)
        self.tankpressurelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.tankpressurelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.tankpressurelabel)

        self.tankpressurelabellayout.addWidget(scroll)
        layout.addLayout(self.tankpressurelabellayout)
        layout.addLayout(self.tankpressuretestbuttonlayout)
        try:
            self.tankpressurebeginbutton = QPushButton("Begin")
            self.tankpressurebeginbutton.setFixedWidth(200)
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)
            self.tankpressuretestbuttonlayout.addWidget(self.tankpressurebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(tankpressure, f"TankPressure")

    def TankPressure(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_tankpressure_step == 0:
                msg1.setWindowTitle("Check Tank")
                msg1.setText("No tank leaks found.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.tankpressure_passed[0] = True
                    self.tankpressure_failed[0] = False
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.tankpressure_passed[0] = False
                    self.tankpressure_failed[0] = True
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_tankpressure_step == 1:
                msg1.setWindowTitle("Check Tank Pressure")
                msg1.setText("<i>Tank pressure is less than 30 PSI as measured by PG2.</i><br><br>")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.tankpressure_passed[1] = True
                    self.tankpressure_failed[1] = False
                    self.tankpressure_completed = True
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.tankpressure_passed[1] = False
                    self.tankpressure_failed[1] = True
                    self.updateTankPressureStep()
                    self.current_tankpressure_step += 1


            # Completed
            elif self.tankpressure_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The TankPressure test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateTankPressureStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateTankPressureStep(self):
        if self.tankpressure_passed[0] or self.tankpressure_failed[0]:
            self.tankpressurelabel.setText(
                "Rotate V7 counterclockwise until PG2 reads below 70 psi.<br><br>"
                "Open V9 periodically to verify pressure is below 70 psi.<br><br>"
                "Close V10.<br><br>"
                "5. Release pressure by opening V11 then remove plug.<br><br>"
                "6. Put pressure relief valve back into the tank using thread seal tape.<br>"
                "Insert plastic drain tube back into original place.<br>"
                "Tighten with 11/16 wrench.<br>"
                "Close V11 and open V10.7.<br><br>"
                "Gradually increase the water pressure to the tank.<br>"
                "Slowly rotate V7 clockwise while watching PG2.<br><br>"
                "The relief valve should remain closed at pressures below 75 psig (5.17 barg).<br><br>"
                "Continue to increase pressure ensuring the valve is fully open prior to or at 100 psig (6.89 barg).<br><br>"
                "8. Disconnect water supply by turning V10 off and drain the Beverage Maker by opening V11.<br><br>"
                "Make sure vent valve operates correctly.<br><br>"
                "Turn V7 counterclockwise to return pressure to 50 psi while periodically opening V9 to verify.<br><br>"
                "Turn V8 horizontal.<br>"
                "Open V9<br><br>"
                "<i>Verify pressure is less than 30 on PG2.</i><br><br>"

            )

            self.tankpressurebeginbutton.setText("Continue")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressure)


        if self.tankpressure_passed[1] or self.tankpressure_failed[1]:
            self.tankpressurelabel.setText(
                "<b>Test Complete</b><br><br>"
                "<b>The Tank Pressure test has been completed successfully!<br><br>"
            )
            self.tankpressurebeginbutton.setText("Results")
            self.tankpressurebeginbutton.clicked.disconnect()
            self.tankpressurebeginbutton.clicked.connect(self.TankPressureResults)

            self.tankpressurerestart = QPushButton("Restart", self)
            self.tankpressurerestart.clicked.connect(self.TankPressureRestart)
            self.tankpressurerestart.setFixedWidth(200)
            self.tankpressuretestbuttonlayout.addWidget(self.tankpressurerestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def TankPressureRestart(self):
        print("Restarting TankPressure Test")

    def TankPressureResults(self):
        print("Printing TankPressure Test Results")