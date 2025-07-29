from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- Resistance Check

class ResistanceTest(QWidget):
    def __init__(self):
        super().__init__()


        self.resistance_passed = [False, False, False]
        self.resistance_failed = [False, False, False]
        self.resistance_completed = False
        self.current_resistance_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        resistancetestbuttonlayout = QHBoxLayout()

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

        self.resistancelabel = QLabel(
            "<b>Turn QuadTech Milliohm Meter on. <br><br>"
            "1. Check resistance from plug lead G to un-anodized brew shelf.</b><br><br> "
            "<i> The millohm meter should not exceed 4.5 milliohms. </i><br><br>"
        )

        self.resistancelabel.setTextFormat(Qt.TextFormat.RichText)
        self.resistancelabel.setWordWrap(True)
        self.resistancelabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.resistancelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.resistancelabel)
        layout.addWidget(scroll)
        layout.addLayout(resistancetestbuttonlayout)
        try:
            self.resistancebeginbutton = QPushButton("Begin")
            self.resistancebeginbutton.setFixedWidth(200)
            self.resistancebeginbutton.clicked.connect(self.Resistance)
            resistancetestbuttonlayout.addWidget(self.resistancebeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(resistance, f"Resistance")

    def Resistance(self):
        try:
            msg1 = QMessageBox()
            msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_resistance_step == 0:
                msg1.setWindowTitle("Check Resistance")
                msg1.setText("Does the milliohm meter read equal to or less than 4.5 milliohms?")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.resistance_passed[0] = True
                    self.resistance_failed[0] = False
                    self.updateResistanceStep()
                    self.current_resistance_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.resistance_passed[0] = False
                    self.resistance_failed[0] = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_resistance_step == 1:
                msg1.setWindowTitle("Check Resistance")
                msg1.setText("Does the milliohm meter read equal to or less than 5.12 milliohms?")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.resistance_passed[1] = True
                    self.resistance_failed[1] = False
                    self.updateResistanceStep()
                    self.current_resistance_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.resistance_passed[1] = False
                    self.resistance_failed[1] = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_resistance_step == 2:
                msg1.setWindowTitle("Check Resistance")
                msg1.setText("Does the milliohm meter read equal to or less than 5.7 milliohms?")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.resistance_passed[2] = True
                    self.resistance_failed[2] = False
                    self.resistance_completed = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.resistance_passed[2] = False
                    self.resistance_failed[2] = True
                    self.updateResistanceStep()
                    self.current_resistance_step += 1

            # Completed
            elif self.resistance_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Resistance test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateResistanceStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateResistanceStep(self):
        if self.resistance_passed[0] or self.resistance_failed[0]:
            self.resistancelabel.setText(
                "<b>2. If applicable, check the resistance from plug lead G to platen heater.</b><br><br>"
                "<i>The milliohm meter should not exceed 5.12 milliohms.</i><br><br>"
            )

            self.resistancebeginbutton.setText("Continue")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.Resistance)

        if self.resistance_passed[1] or self.resistance_failed[1]:
            self.resistancelabel.setText(
                "<b>3. Connect a resistance bridge between plug lead F and faucet.</b><br><br>"
                "<i>The milliohm meter should not exceed 5.7 milliohms.</i><br><br>"
            )

            self.resistancebeginbutton.setText("Continue")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.Resistance)

        if self.resistance_passed[2] or self.resistance_failed[2]:
            self.resistancelabel.setText(
                "<b>Resistance Test Completed!</b><br><br>"
                "<b>Please Disconnect the IAS11003C plug from PP1 and turn off the milliohm meter.<br><br>"
            )
            self.resistancebeginbutton.setText("Results")
            self.resistancebeginbutton.clicked.disconnect()
            self.resistancebeginbutton.clicked.connect(self.ResistanceResults)

            self.resistancerestart = QPushButton("Restart", self)
            self.resistancerestart.clicked.connect(self.ResistanceRestart)
            self.resistancerestart.setFixedWidth(200)
            self.resistancetestbuttonlayout.addWidget(self.resistancerestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def ResistanceRestart(self):
        print("Restarting Resistance Test")

    def ResistanceResults(self):
        print("Printing Resistance Test Results")

