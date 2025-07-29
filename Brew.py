from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- Brew Check

class BrewTest(QWidget):
    def __init__(self):
        super().__init__()


        self.brew_passed = [False, False, False]
        self.brew_failed = [False, False, False]
        self.brew_completed = False
        self.current_brew_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.brewtestbuttonlayout = QHBoxLayout()

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

        self.brewlabel = QLabel(
            "<b> <br><br>"
            "Brew step one.</b><br><br> "
            "<i> Brew condition one.</i><br><br>"
        )

        self.brewlabel.setTextFormat(Qt.TextFormat.RichText)
        self.brewlabel.setWordWrap(True)
        self.brewlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.brewlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.brewlabel)
        layout.addWidget(scroll)
        layout.addLayout(self.brewtestbuttonlayout)
        try:
            self.brewbeginbutton = QPushButton("Begin")
            self.brewbeginbutton.setFixedWidth(200)
            self.brewbeginbutton.clicked.connect(self.Brew)
            self.brewtestbuttonlayout.addWidget(self.brewbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(brew, f"Brew")

    def Brew(self):
        try:
            msg1 = QMessageBox()
            msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_brew_step == 0:
                msg1.setWindowTitle("Check Brew")
                msg1.setText("Brew step one.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.brew_passed[0] = True
                    self.brew_failed[0] = False
                    self.updateBrewStep()
                    self.current_brew_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.brew_passed[0] = False
                    self.brew_failed[0] = True
                    self.updateBrewStep()
                    self.current_brew_step += 1

            # STEP 2 — 5.12 mΩ
            elif self.current_brew_step == 1:
                msg1.setWindowTitle("Check Brew")
                msg1.setText("Brew step two.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.brew_passed[1] = True
                    self.brew_failed[1] = False
                    self.updateBrewStep()
                    self.current_brew_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.brew_passed[1] = False
                    self.brew_failed[1] = True
                    self.updateBrewStep()
                    self.current_brew_step += 1

            # STEP 3 — 5.7 mΩ
            elif self.current_brew_step == 2:
                msg1.setWindowTitle("Check Brew")
                msg1.setText("Brew step three.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.brew_passed[2] = True
                    self.brew_failed[2] = False
                    self.brew_completed = True
                    self.updateBrewStep()
                    self.current_brew_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.brew_passed[2] = False
                    self.brew_failed[2] = True
                    self.updateBrewStep()
                    self.current_brew_step += 1

            # Completed
            elif self.brew_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The Brew test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateBrewStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateBrewStep(self):
        if self.brew_passed[0] or self.brew_failed[0]:
            self.brewlabel.setText(
                "<b>Brew step two.</b><br><br>"
                "<i>Brew condition two.</i><br><br>"
            )

            self.brewbeginbutton.setText("Continue")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.Brew)

        if self.brew_passed[1] or self.brew_failed[1]:
            self.brewlabel.setText(
                "<b>Brew step three.</b><br><br>"
                "<i>Brew condition three.</i><br><br>"
            )

            self.brewbeginbutton.setText("Continue")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.Brew)

        if self.brew_passed[2] or self.brew_failed[2]:
            self.brewlabel.setText(
                "<b>Brew Test Completed!</b><br><br>"
                "<b>Brew completion step.<br><br>"
            )
            self.brewbeginbutton.setText("Results")
            self.brewbeginbutton.clicked.disconnect()
            self.brewbeginbutton.clicked.connect(self.BrewResults)

            self.brewrestart = QPushButton("Restart", self)
            self.brewrestart.clicked.connect(self.BrewRestart)
            self.brewrestart.setFixedWidth(200)
            self.brewtestbuttonlayout.addWidget(self.brewrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def BrewRestart(self):
        print("Restarting Brew Test")

    def BrewResults(self):
        print("Printing Brew Test Results")