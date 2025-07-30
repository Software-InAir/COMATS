from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- RTDCircuit Check

class RTDCircuitTest(QWidget):
    rtdcircuit_results = "Some RTD Circuit Results!"
    def __init__(self):
        super().__init__()


        self.rtdcircuit_passed = [False, False, False, False]
        self.rtdcircuit_failed = [False, False, False, False]
        self.rtdcircuit_completed = False
        self.current_rtdcircuit_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.rtdcircuitlabellayout = QHBoxLayout()
        self.rtdcircuittestbuttonlayout = QHBoxLayout()

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

        self.rtdcircuitlabel = QLabel(
            "<b>1. With the Beverage Maker connected to the water supply and the red lever on the EDB in the OFF position,"
            " remove the cover from the power module assy and disconnect the RTD assy plug (P4) from the J4"
            " connector on the controller board assy.<br><br>"
            "2. Connect the DMM (set to ohms scale) to the RTD simulator harness (IAS11003A).<br><br>"
            "Rotate the knob until 1430±1 ohms is indicated on the DMM.<br><br>"
            "Change DMM to DC volts then connect harness inline between the controller board assy (J4) and P4.<br><br>"
            "3. Connect the Beverage Maker to the power supply.<br><br>"
            "Set the red lever on the EDB to the ON position.<br><br>"
            "4. Press the power button.<br><br>"
            "<i>This should trip the safety latch.</i><br><br>"
            "<i>(If the safety latch is tripped, there will be no current drawn to the heaters and the power indicator light should go into double-blink mode.)</i><br><br>"
            )

        self.rtdcircuitlabel.setTextFormat(Qt.TextFormat.RichText)
        self.rtdcircuitlabel.setWordWrap(True)
        self.rtdcircuitlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.rtdcircuitlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.rtdcircuitlabel)

        self.rtdcircuitlabellayout.addWidget(scroll)
        layout.addLayout(self.rtdcircuitlabellayout)
        layout.addLayout(self.rtdcircuittestbuttonlayout)
        try:
            self.rtdcircuitbeginbutton = QPushButton("Begin")
            self.rtdcircuitbeginbutton.setFixedWidth(200)
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(rtdcircuit, f"RTDCircuit")

    def RTDCircuit(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_rtdcircuit_step == 0:
                msg1.setWindowTitle("Safety Latch Check")
                msg1.setText("Safety Latch did not engage.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.rtdcircuit_passed[0] = True
                    self.rtdcircuit_failed[0] = False
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.rtdcircuit_passed[0] = False
                    self.rtdcircuit_failed[0] = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_rtdcircuit_step == 1:
                msg1.setWindowTitle("Safety Latch Check")
                msg1.setText("Safety Latch did not engage.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.rtdcircuit_passed[1] = True
                    self.rtdcircuit_failed[1] = False
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.rtdcircuit_passed[1] = False
                    self.rtdcircuit_failed[1] = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_rtdcircuit_step == 2:
                msg1.setWindowTitle("Check DMM")
                msg1.setText("DMM reads less than 2.060 volts.<br><br>")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.rtdcircuit_passed[2] = True
                    self.rtdcircuit_failed[2] = False
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.rtdcircuit_passed[2] = False
                    self.rtdcircuit_failed[2] = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # STEP 4 — 5.7 mΩ
            elif self.current_rtdcircuit_step == 3:
                    msg1.setWindowTitle("Safety Latch Check")
                    msg1.setText("Safety Latch not engaged.<br><br>")
                    pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                    fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                    msg1.exec()

                    if msg1.clickedButton() == pass_button:
                        self.rtdcircuit_passed[3] = True
                        self.rtdcircuit_failed[3] = False
                        self.rtdcircuit_completed = True
                        self.updateRTDCircuitStep()
                        self.current_rtdcircuit_step += 1
                    elif msg1.clickedButton() == fail_button:
                        self.rtdcircuit_passed[3] = False
                        self.rtdcircuit_failed[3] = True
                        self.updateRTDCircuitStep()
                        self.current_rtdcircuit_step += 1

            # Completed
            elif self.rtdcircuit_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The RTD Circuit test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateRTDCircuitStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateRTDCircuitStep(self):
        if self.rtdcircuit_passed[0] or self.rtdcircuit_failed[0]:
            self.rtdcircuitlabel.setText(
                "5. Rotate the knob counterclockwise until 2.365±0.003 volts is shown on the DMM.<br><br>"
                "6. Press the power button to turn the Beverage Maker off. <br><br>"
                "7. Reset the safety latch by pressing the manual switch on the back of the power module assy under the grommet.<br><br>"
                "8. Press the power button.<br>"
                "<i>While no current is being drawn by the heaters, the safety latch should not trip and the power indicator light should not go into double-blink mode.</i><br><br>"
                "<i>(Observe for 10 seconds.)</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[1] or self.rtdcircuit_failed[1]:
            self.rtdcircuitlabel.setText(
                "9. Rotate the knob on IAS11003A counterclockwise until DMM reads 2.100 volts.<br><br>"
                "While monitoring the current drawn by the heaters, slowly rotate the knob until no current is drawn by the heaters (readings of ~0 A for each phase).<br><br>"
                "<i>The voltage on the DMM should be less than 2.060 volts.</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[2] or self.rtdcircuit_failed[2]:
            self.rtdcircuitlabel.setText(
                "10. Press the POWER button to turn off the Beverage Maker.<br><br>"
                "Set the red lever on the EDB to the OFF position.<br><br>"
                "11. Disconnect the IAS11003A from the controller board assy.<br><br>"
                "Connect the P4 to the controller board assy (J4).<br><br>"
                "12. Put the cover on the power module assy.<br><br>"
                "13. Set the red lever on the EDB to the ON position.<br><br>"
                "14. Press the power button.<br><br> "
                "<i>This should not trip the safety latch.</i><br>"
                "<i>(Make sure the power indicator light does not go into double-blink mode.)</i>"

            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[3] or self.rtdcircuit_failed[3]:
            self.rtdcircuitlabel.setText(
                "<b>Test Complete.<br>"
                "The RTD Circuit Test has been completed successfully!<br><br>"
                "Please press the POWER button to turn off the Beverage Maker.</b><br><br>"
                )

            self.rtdcircuitbeginbutton.setText("Results")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuitResults)

            self.rtdcircuitrestart = QPushButton("Restart", self)
            self.rtdcircuitrestart.clicked.connect(self.RTDCircuitRestart)
            self.rtdcircuitrestart.setFixedWidth(200)
            self.rtdcircuittestbuttonlayout.addWidget(self.rtdcircuitrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def RTDCircuitRestart(self):
        print("Restarting RTDCircuit Test")

    def RTDCircuitResults(self):
        print("Printing RTDCircuit Test Results")