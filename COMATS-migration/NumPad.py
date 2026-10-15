from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QPushButton, QHBoxLayout, QMessageBox


class NumericKeypadDialog(QDialog):
    def __init__(
        self,
        parent=None,
        title: str = "Enter value",
        label: str = "Value:",
        initial: float = 0.0,
        min_value: float = 0.0,
        max_value: float = 1_000_000.0,
        decimals: int = 2,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals

        main_layout = QVBoxLayout(self)

        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(label_widget)

        # Display field
        self.edit = QLineEdit(self)
        self.edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.edit.setReadOnly(True)          # user uses keypad, not keyboard
        self.edit.setText(f"{initial:.{decimals}f}")
        self.edit.setFont(QFont("Segoe UI", 18))
        main_layout.addWidget(self.edit)

        # Keypad grid
        grid = QGridLayout()

        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            (".", 3, 0), ("0", 3, 1), ("←", 3, 2),
        ]

        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setMinimumSize(70, 70)
            btn.clicked.connect(self.handle_button)
            grid.addWidget(btn, row, col)

        main_layout.addLayout(grid)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_value)
        bottom_layout.addWidget(clear_btn)

        bottom_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept_value)
        bottom_layout.addWidget(ok_btn)

        main_layout.addLayout(bottom_layout)

        # Make it big-ish for touch
        self.resize(350, 450)

    def handle_button(self):
        sender = self.sender()
        if not sender:
            return

        text = sender.text()
        current = self.edit.text()

        if text == "←":  # backspace
            self.edit.setText(current[:-1])
            return

        if text == ".":
            if "." in current:
                return  # only one decimal
            if not current:
                current = "0"  # start with 0.
            self.edit.setText(current + ".")
            return

        # number 0-9
        self.edit.setText(current + text)

    def clear_value(self):
        self.edit.clear()

    def accept_value(self):
        txt = self.edit.text().strip()
        if txt in ("", ".", "-"):
            val = 0.0
        else:
            try:
                val = float(txt)
            except ValueError:
                QMessageBox.warning(self, "Invalid value", "Please enter a valid number.")
                return

        if not (self.min_value <= val <= self.max_value):
            QMessageBox.warning(
                self,
                "Out of range",
                f"Value must be between {self.min_value} and {self.max_value}.",
            )
            return

        # Normalize formatting
        self.edit.setText(f"{val:.{self.decimals}f}")
        self.accept()

    def value(self) -> float:
        try:
            return float(self.edit.text())
        except ValueError:
            return 0.0

    @staticmethod
    def getValue(
            parent=None,
            title: str = "Enter value",
            label: str = "Value:",
            initial: float = 0,
            min_value: float = 0.0,
            max_value: float = 1_000_000.0,
            decimals: int = 2,
    ):
        dlg = NumericKeypadDialog(
            parent=parent,
            title=title,
            label=label,
            initial=initial,
            min_value=min_value,
            max_value=max_value,
            decimals=decimals,
        )
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            return dlg.value(), True
        else:
            return initial, False