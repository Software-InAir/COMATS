from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- PowerAndLowLight Check

class PowerAndLowLightTest(QWidget):
    powerandlowlight_results = "Some Power and Low Light Results!"
    def __init__(self):
        super().__init__()


        self.powerandlowlight_passed = [False, False, False, False, False]
        self.powerandlowlight_failed = [False, False, False, False, False]
        self.powerandlowlight_completed = False
        self.current_powerandlowlight_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.powerandlowlightlayout = QHBoxLayout()

        self.powerandlowlighttestbuttonlayout = QHBoxLayout()

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

        self.powerandlowlightlabel = QLabel(
            "1. Connect the Beverage Maker to the power supply.<br><br>"
            "<i>Ensure EDB is in the ON position.</i><br><br>"
            "2. If connected, disconnect the water supply from the Beverage Maker by closing V10 and opening V11.<br><br>"
            "3. Press the power button.<br><br>"
            "4.<i>>Both the power and low water indicators should be lit without the heaters activating "
            "<br>(as indicated by ~0 A readings for each phase of the power supply).</i><br><br>"
        )

        self.powerandlowlightlabel.setTextFormat(Qt.TextFormat.RichText)
        self.powerandlowlightlabel.setWordWrap(True)
        self.powerandlowlightlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.powerandlowlightlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.powerandlowlightlabel)


        self.powerandlowlightlayout.addWidget(scroll)
        layout.addLayout(self.powerandlowlightlayout)
        layout.addLayout(self.powerandlowlighttestbuttonlayout)
        try:
            self.powerandlowlightbeginbutton = QPushButton("Begin")
            self.powerandlowlightbeginbutton.setFixedWidth(200)
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)
            self.powerandlowlighttestbuttonlayout.addWidget(self.powerandlowlightbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(powerandlowlight, f"PowerAndLowLight")

    def PowerAndLowLight(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_powerandlowlight_step == 0:
                msg1.setWindowTitle("Power and Low Light Indicators")
                msg1.setText("<i>Power and Low Light Indicators activated.</i><br><br>")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.powerandlowlight_passed[0] = True
                    self.powerandlowlight_failed[0] = False
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.powerandlowlight_passed[0] = False
                    self.powerandlowlight_failed[0] = True
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_powerandlowlight_step == 1:
                msg1.setWindowTitle("Power Indicator Deactivated")
                msg1.setText("The power indicator light has been deactivated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.powerandlowlight_passed[1] = True
                    self.powerandlowlight_failed[1] = False
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.powerandlowlight_passed[1] = False
                    self.powerandlowlight_failed[1] = True
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_powerandlowlight_step == 2:
                msg1.setWindowTitle("Power Indicator Activated")
                msg1.setText("The power indicator light has been activated.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.powerandlowlight_passed[2] = True
                    self.powerandlowlight_failed[2] = False
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.powerandlowlight_passed[2] = False
                    self.powerandlowlight_failed[2] = True
                    self.updatePowerAndLowLightStep()
                    self.current_powerandlowlight_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_powerandlowlight_step == 3:
                    msg1.setWindowTitle("Power Indicator Deactivated")
                    msg1.setText("The power indicator light has been deactivated.")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        self.powerandlowlight_passed[3] = True
                        self.powerandlowlight_failed[3] = False
                        self.powerandlowlight_completed = True
                        self.updatePowerAndLowLightStep()
                        self.current_powerandlowlight_step += 1
                    elif msg1.clickedButton() == fail_button:
                        self.powerandlowlight_passed[3] = False
                        self.powerandlowlight_failed[3] = True
                        self.powerandlowlight_completed = True
                        self.updatePowerAndLowLightStep()
                        self.current_powerandlowlight_step += 1


            # Completed
            elif self.powerandlowlight_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Power And Low Light Indicator test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updatePowerAndLowLightStep()

        except Exception as e:
            print(f"Error: {e}")

    def updatePowerAndLowLightStep(self):
        if self.powerandlowlight_passed[0] or self.powerandlowlight_failed[0]:
            self.powerandlowlightlabel.setText(
                "5. Press the POWER button.<br><br>"
                "<i>Power indicator should deactivate.</i><br><br>"
            )

            self.powerandlowlightbeginbutton.setText("Continue")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)

        if self.powerandlowlight_passed[1] or self.powerandlowlight_failed[1]:
            self.powerandlowlightlabel.setText(
                "6. Connect the water supply to the Beverage Maker by closing V11 and opening V10.<br><br>"
                "Once filled, ensure water pressure is set between 24 and 29 psig by assessing reading on PG2 (1.66 to 2.0 barg).<br><br>"
                "7. Make sure the Beverage Maker tank fills and no leaks are present. (A full tank is indicated by a reading of 0 on the flow meter (FM))<br><br>"
                "8. After the tank is filled, press the power button.<br><br>"
                "<i>The power indicator light should be activated.</i><br><br>"

            )

            self.powerandlowlightbeginbutton.setText("Continue")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)

        if self.powerandlowlight_passed[2] or self.powerandlowlight_failed[2]:
            self.powerandlowlightlabel.setText(
                "Make sure the LOW WATER indicator light is off and press the power button.<br><br>"
                "<i>The power light indicator should be deactivated.</i><br><br>"
            )
            self.powerandlowlightbeginbutton.setText("Continue")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLight)


        if self.powerandlowlight_passed[3] or self.powerandlowlight_failed[3]:
            self.powerandlowlightlabel.setText(
                "Test completed.<br><br>"
                "<i>The Power and Low Light indicator Test has been completed succssfully!</i><br><br>"
                )
            self.powerandlowlightbeginbutton.setText("Results")
            self.powerandlowlightbeginbutton.clicked.disconnect()
            self.powerandlowlightbeginbutton.clicked.connect(self.PowerAndLowLightResults)

            self.powerandlowlightrestart = QPushButton("Restart", self)
            self.powerandlowlightrestart.clicked.connect(self.PowerAndLowLightRestart)
            self.powerandlowlightrestart.setFixedWidth(200)
            self.powerandlowlighttestbuttonlayout.addWidget(self.powerandlowlightrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def PowerAndLowLightRestart(self):
        print("Restarting PowerAndLowLight Test")

    def PowerAndLowLightResults(self):
        print("Printing PowerAndLowLight Test Results")