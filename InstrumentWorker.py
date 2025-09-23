from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot, Qt

class InstrumentWorker(QObject):
    ch1 = pyqtSignal(float)
    ch2 = pyqtSignal(float)
    ch3 = pyqtSignal(float)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, resource_name: str, poll_ms: int = 200, parent=None):
        super().__init__(parent)
        self._resource_name = resource_name
        self._poll_ms = poll_ms
        self._rm = None
        self._dev = None
        self._timer = None
        self._polling = False

    @pyqtSlot()
    def start(self):
        # open VISA here (worker thread context)
        import pyvisa
        try:
            self._rm = pyvisa.ResourceManager()
            self._dev = self._rm.open_resource(self._resource_name)
            # self._dev.read_termination = '\n'
            # self._dev.write_termination = '\n'
            self._dev.timeout = 1000
            self.status.emit(f"Opened {self._resource_name}")
        except Exception as e:
            self.status.emit(f"VISA open failed: {e}")
            self.finished.emit()
            return

        self._timer = QTimer()
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._poll_once)
        self.status.emit("Instrument worker ready")
        self.start_polling()

    @pyqtSlot()
    def start_polling(self):
        if self._timer and not self._polling:
            self._polling = True
            self._timer.start(self._poll_ms)
            self.status.emit(f"Polling started @ {self._poll_ms} ms")

    @pyqtSlot()
    def stop_polling(self):
        if self._timer and self._polling:
            self._timer.stop()
            self._polling = False
            self.status.emit("Polling stopped")

    @pyqtSlot(int)
    def set_interval_ms(self, ms: int):
        self._poll_ms = max(10, ms)
        if self._timer and self._polling:
            self._timer.start(self._poll_ms)
            self.status.emit(f"Poll interval set to {self._poll_ms} ms")

    @pyqtSlot(str)
    def write(self, scpi: str):
        try:
            self._dev.write(scpi)
        except Exception as e:
            self.status.emit(f"Write error: {e}")

    @pyqtSlot(str)
    def query_text(self, scpi: str):
        try:
            resp = self._dev.query(scpi).strip()
            self.status.emit(f"{scpi} -> {resp}")
        except Exception as e:
            self.status.emit(f"Query error: {e}")

    @pyqtSlot()
    def _poll_once(self):
        try:
            v1 = float(self._dev.query('MEAS:CURR 1?').strip())
            v2 = float(self._dev.query('MEAS:CURR 2?').strip())
            v3 = float(self._dev.query('MEAS:CURR 3?').strip())
            self.ch1.emit(v1)
            self.ch2.emit(v2)
            self.ch3.emit(v3)
        except Exception as e:
            self.status.emit(f"Poll error: {e}")

    @pyqtSlot()
    def shutdown(self):
        try:
            if self._timer:
                self._timer.stop()
            if self._dev:
                self._dev.close()
            if self._rm:
                self._rm.close()
        except Exception as e:
            self.status.emit(f"Close warning: {e}")
        self.finished.emit()
