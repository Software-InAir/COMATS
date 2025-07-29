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
    def __init__(self):
        super().__init__()


        self.rtdcircuit_passed = [False, False, False]
        self.rtdcircuit_failed = [False, False, False]
        self.rtdcircuit_completed = False
        self.current_rtdcircuit_step = 0

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)

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
            "<b> <br><br>"
            "RTDCircuit step one.</b><br><br> "
            "<i> RTDCircuit condition one.</i><br><br>"
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
        layout.addWidget(scroll)
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
            msg1.setIcon(QMessageBox.Icon.Information)

            # STEP 1 — 4.5 mΩ
            if self.current_rtdcircuit_step == 0:
                msg1.setWindowTitle("Check RTDCircuit")
                msg1.setText("RTDCircuit step one.")
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
                msg1.setWindowTitle("Check RTDCircuit")
                msg1.setText("RTDCircuit step two.")
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
                msg1.setWindowTitle("Check RTDCircuit")
                msg1.setText("RTDCircuit step three.")
                pass_button = msg1.addButton("Pass", QMessageBox.ButtonRole.AcceptRole)
                fail_button = msg1.addButton("Fail", QMessageBox.ButtonRole.RejectRole)
                msg1.exec()

                if msg1.clickedButton() == pass_button:
                    self.rtdcircuit_passed[2] = True
                    self.rtdcircuit_failed[2] = False
                    self.rtdcircuit_completed = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1
                elif msg1.clickedButton() == fail_button:
                    self.rtdcircuit_passed[2] = False
                    self.rtdcircuit_failed[2] = True
                    self.updateRTDCircuitStep()
                    self.current_rtdcircuit_step += 1

            # Completed
            elif self.rtdcircuit_completed:
                msg1.setWindowTitle("Test Completed!")
                msg1.setText("The RTDCircuit test has been completed successfully.")
                msg1.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
                msg1.exec()

                self.updateRTDCircuitStep()

        except Exception as e:
            print(f"Error: {e}")

    def updateRTDCircuitStep(self):
        if self.rtdcircuit_passed[0] or self.rtdcircuit_failed[0]:
            self.rtdcircuitlabel.setText(
                "<b>RTDCircuit step two.</b><br><br>"
                "<i>RTDCircuit condition two.</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[1] or self.rtdcircuit_failed[1]:
            self.rtdcircuitlabel.setText(
                "<b>RTDCircuit step three.</b><br><br>"
                "<i>RTDCircuit condition three.</i><br><br>"
            )

            self.rtdcircuitbeginbutton.setText("Continue")
            self.rtdcircuitbeginbutton.clicked.disconnect()
            self.rtdcircuitbeginbutton.clicked.connect(self.RTDCircuit)

        if self.rtdcircuit_passed[2] or self.rtdcircuit_failed[2]:
            self.rtdcircuitlabel.setText(
                "<b>RTDCircuit Test Completed!</b><br><br>"
                "<b>RTDCircuit completion step.<br><br>"
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