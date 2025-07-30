from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------------------------------------------------------- Dielectric Test
class DielectricTest(QWidget):
        dielectric_results = f""

        def __init__(self):
                super().__init__()

                #temp phase
                phase1read = .47
                phase2read = .39
                phase3read = .26



                self.dielectric_passed = [False, False]
                self.dielectric_failed = [False, False]
                self.dielectric_completed = False

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


                phaselayout = QHBoxLayout()
                #phaselayout.setContentsMargins(0, 100, 0, 0)

                spacer1 = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                layout.addSpacerItem(spacer1)

                spacer2 = QSpacerItem(720, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
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




                self.setLayout(layout)

        def Dielectric(self):

                try:
                        if not self.dielectric_passed[0] and not self.dielectric_failed[0]:
                                msg1 = QMessageBox()
                                msg1.setWindowTitle("Check Current")
                                msg1.setText(
                                        "Current flow should not exceed a maximum of 2.0 milliamperes during the test period.")
                                #msg1.setIcon(QMessageBox.Icon.Information)

                                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)

                                msg1.exec()

                                if msg1.clickedButton() == pass_button:
                                        self.dielectric_passed[0] = True
                                        self.dielectric_failed[0] = False
                                        self.updateDielectricStep()
                                elif msg1.clickedButton() == fail_button:
                                        self.dielectric_passed[0] = False
                                        self.dielectric_failed[0] = True
                                        self.updateDielectricStep()


                        elif self.dielectric_passed[0] or self.dielectric_failed[0]:
                                msg1 = QMessageBox()
                                msg1.setWindowTitle("Check Current")
                                msg1.setText("Does megaohmmeter read greater than 2?")
                                #msg1.setIcon(QMessageBox.Icon.Information)

                                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)

                                msg1.exec()

                                if msg1.clickedButton() == pass_button:
                                        self.dielectric_passed[1] = True
                                        self.dielectric_failed[1] = False
                                        self.dielectric_completed = True
                                        self.updateDielectricStep()
                                elif msg1.clickedButton() == fail_button:
                                        self.dielectric_passed[1] = False
                                        self.dielectric_failed[1] = True
                                        self.updateDielectricStep()


                        elif self.dielectric_completed:
                                msg1 = QMessageBox()
                                msg1.setWindowTitle("Test Completed!")
                                msg1.setText("The dielectric test has been completed successfully.")
                                #msg1.setIcon(QMessageBox.Icon.Information)

                                pass_button = msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)

                                msg1.exec()

                except Exception as e:
                        print(f"Error: {e}")

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

        def DielectricRestart(self):
                print("Restarting Dielectric Test")

        def DielectricResults(self):
                print("Printing Dielectric Test Results")
