from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget,
    QPushButton, QLineEdit, QScrollArea, QMessageBox
)

from PyQt6.QtCore import Qt

#-------- temp phase
phase1read = 0.36
phase2read = 0.42
phase3read = 0.39

#------------------------------------------------------- ServerRetainer Check

class ServerRetainerTest(QWidget):
    serverretainer_results = "Some Server Retainer Results"
    def __init__(self):
        super().__init__()


        self.serverretainer_passed = [False, False, False]
        self.serverretainer_failed = [False, False, False]
        self.serverretainer_completed = False
        self.current_serverretainer_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

        self.serverretainerlabellayout = QHBoxLayout()
        self.serverretainertestbuttonlayout = QHBoxLayout()

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

        self.serverretainerlabel = QLabel(
            "<b>With a server and the brew cup installed, lower the brew handle.<br><br>"
            "Pull on the server to make sure the server retainer is working correctly.</b><br><br>"
            "<i>Server should remain firmly in place</i><br><br>"


        )

        self.serverretainerlabel.setTextFormat(Qt.TextFormat.RichText)
        self.serverretainerlabel.setWordWrap(True)
        self.serverretainerlabel.setStyleSheet("""
                                    font-size: 18px;
                                    padding-top: 50px;
                                    padding-left: 50px;
                                    padding-right: 50px;
                                    padding-bottom: 50px;
                                    """)
        self.serverretainerlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.serverretainerlabel)


        self.serverretainerlabellayout.addWidget(scroll)
        layout.addLayout(self.serverretainerlabellayout)
        layout.addLayout(self.serverretainertestbuttonlayout)
        try:
            self.serverretainerbeginbutton = QPushButton("Begin")
            self.serverretainerbeginbutton.setFixedWidth(200)
            self.serverretainerbeginbutton.clicked.connect(self.ServerRetainer)
            self.serverretainertestbuttonlayout.addWidget(self.serverretainerbeginbutton, alignment=Qt.AlignmentFlag.AlignCenter)

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
        #tabs.addTab(serverretainer, f"ServerRetainer")

    def ServerRetainer(self):
        try:
            msg1 = QMessageBox()
            #msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_serverretainer_step == 0:
                msg1.setWindowTitle("Check Server Retainer")
                msg1.setText("Server remains in place.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.serverretainer_passed[0] = True
                    self.serverretainer_failed[0] = False
                    self.serverretainer_completed = True
                    self.updateServerRetainerStep()
                    self.current_serverretainer_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.serverretainer_passed[0] = False
                    self.serverretainer_failed[0] = True
                    self.updateServerRetainerStep()
                    self.current_serverretainer_step += 1


            # Completed
            elif self.serverretainer_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The ServerRetainer test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateServerRetainerStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateServerRetainerStep(self):

        if self.serverretainer_passed[0] or self.serverretainer_failed[0]:
            self.serverretainerlabel.setText(
                "<b>Test Completed</b><br><br>"
                "The Server Retainer test has been completed successfully!</b><br><br>"
            )
            self.serverretainerbeginbutton.setText("Results")
            self.serverretainerbeginbutton.clicked.disconnect()
            self.serverretainerbeginbutton.clicked.connect(self.ServerRetainerResults)

            self.serverretainerrestart = QPushButton("Restart", self)
            self.serverretainerrestart.clicked.connect(self.ServerRetainerRestart)
            self.serverretainerrestart.setFixedWidth(200)
            self.serverretainertestbuttonlayout.addWidget(self.serverretainerrestart, alignment=Qt.AlignmentFlag.AlignCenter)

    def ServerRetainerRestart(self):
        print("Restarting ServerRetainer Test")

    def ServerRetainerResults(self):
        print("Printing ServerRetainer Test Results")