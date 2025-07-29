from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- HeaterAndPreheater Check

class HeaterAndPreheaterTest(QWidget):
    def __init__(self):
        super().__init__()


        self.heaterandpreheater_passed = [False, False, False]
        self.heaterandpreheater_failed = [False, False, False]
        self.heaterandpreheater_completed = False
        self.current_heaterandpreheater_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        heaterandpreheatertestbuttonlayout = QHBoxLayout()

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

        self.heaterandpreheaterlabel = QLabel(
            "<b> <br><br>"
            "HeaterAndPreheater step one.</b><br><br> "
            "<i> HeaterAndPreheater condition one.</i><br><br>"
        )

        self.heaterandpreheaterlabel.setTextFormat(Qt.TextFormat.RichText)
        self.heaterandpreheaterlabel.setWordWrap(True)
        self.heaterandpreheaterlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.heaterandpreheaterlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.heaterandpreheaterlabel)
        layout.addWidget(scroll)
        layout.addLayout(heaterandpreheatertestbuttonlayout)
        try:
            self.heaterandpreheaterbeginbutton = QPushButton("Begin")
            self.heaterandpreheaterbeginbutton.setFixedWidth(200)
            self.heaterandpreheaterbeginbutton.clicked.connect(self.HeaterAndPreheater)
            heaterandpreheatertestbuttonlayout.addWidget(self.heaterandpreheaterbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(heaterandpreheater, f"HeaterAndPreheater")

    def HeaterAndPreheater(self):
        try:
            msg1 = QMessageBox()
            msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_heaterandpreheater_step == 0:
                msg1.setWindowTitle("Check HeaterAndPreheater")
                msg1.setText("HeaterAndPreheater step one.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.heaterandpreheater_passed[0] = True
                    self.heaterandpreheater_failed[0] = False
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.heaterandpreheater_passed[0] = False
                    self.heaterandpreheater_failed[0] = True
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_heaterandpreheater_step == 1:
                msg1.setWindowTitle("Check HeaterAndPreheater")
                msg1.setText("HeaterAndPreheater step two.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.heaterandpreheater_passed[1] = True
                    self.heaterandpreheater_failed[1] = False
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.heaterandpreheater_passed[1] = False
                    self.heaterandpreheater_failed[1] = True
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_heaterandpreheater_step == 2:
                msg1.setWindowTitle("Check HeaterAndPreheater")
                msg1.setText("HeaterAndPreheater step three.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.heaterandpreheater_passed[2] = True
                    self.heaterandpreheater_failed[2] = False
                    self.heaterandpreheater_completed = True
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.heaterandpreheater_passed[2] = False
                    self.heaterandpreheater_failed[2] = True
                    self.updateHeaterAndPreheaterStep()
                    self.current_heaterandpreheater_step += 1

            # Completed
            elif self.heaterandpreheater_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The HeaterAndPreheater test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateHeaterAndPreheaterStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateHeaterAndPreheaterStep(self):
        if self.heaterandpreheater_passed[0] or self.heaterandpreheater_failed[0]:
            self.heaterandpreheaterlabel.setText(
                "<b>HeaterAndPreheater step two.</b><br><br>"
                "<i>HeaterAndPreheater condition two.</i><br><br>"
            )

            self.heaterandpreheaterbeginbutton.setText("Continue")
            self.heaterandpreheaterbeginbutton.clicked.disconnect()
            self.heaterandpreheaterbeginbutton.clicked.connect(self.HeaterAndPreheater)

        if self.heaterandpreheater_passed[1] or self.heaterandpreheater_failed[1]:
            self.heaterandpreheaterlabel.setText(
                "<b>HeaterAndPreheater step three.</b><br><br>"
                "<i>HeaterAndPreheater condition three.</i><br><br>"
            )

            self.heaterandpreheaterbeginbutton.setText("Continue")
            self.heaterandpreheaterbeginbutton.clicked.disconnect()
            self.heaterandpreheaterbeginbutton.clicked.connect(self.HeaterAndPreheater)

        if self.heaterandpreheater_passed[2] or self.heaterandpreheater_failed[2]:
            self.heaterandpreheaterlabel.setText(
                "<b>HeaterAndPreheater Test Completed!</b><br><br>"
                "<b>HeaterAndPreheater completion step.<br><br>"
            )
            self.heaterandpreheaterbeginbutton.setText("Results")
            self.heaterandpreheaterbeginbutton.clicked.disconnect()
            self.heaterandpreheaterbeginbutton.clicked.connect(self.HeaterAndPreheaterResults)

            self.heaterandpreheaterrestart = QPushButton("Restart", self)
            self.heaterandpreheaterrestart.clicked.connect(self.HeaterAndPreheaterRestart)
            self.heaterandpreheaterrestart.setFixedWidth(200)
            self.heaterandpreheatertestbuttonlayout.addWidget(self.heaterandpreheaterrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def HeaterAndPreheaterRestart(self):
        print("Restarting HeaterAndPreheater Test")

    def HeaterAndPreheaterResults(self):
        print("Printing HeaterAndPreheater Test Results")
