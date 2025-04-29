import sys
import os
import time
import pyvisa
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from threading import Thread
import numpy as np
from multiprocessing import Process


from analysis_window import launch_plot_from_data

# from analysis_window_pyqt_v2 import launch_plot_from_data

# =============================================================================
# SweepWorker: Performs an adaptive IV sweep on the instrument.
# =============================================================================
class SweepWorker(QtCore.QObject):
    # Signals emitted during the sweep:
    # new_data: emits a tuple (voltage, current) each time new measurement is obtained.
    # finished: emitted when the sweep is complete.
    # error: emitted when an error occurs, with an error message.
    new_data = QtCore.pyqtSignal(float, float)
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    
    def __init__(self, instrument, current_limit, min_voltage, max_voltage, sensitivity):
        """
        Initialize the SweepWorker with instrument parameters.
        """
        super().__init__()
        self.instrument = instrument
        self.current_limit = current_limit
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage
        self.sensitivity = sensitivity
        self._paused = False
        self._running = True

    @QtCore.pyqtSlot()
    def run(self):
        """
        This slot performs the IV sweep. It configures the instrument, 
        then steps through voltage values using an adaptive step-size.
        """
        try:
            # Reset and configure the instrument
            self.instrument.write("*RST")
            time.sleep(0.25)
            self.instrument.write("SOURce:FUNCtion:MODE VOLTage")
            time.sleep(0.1)
            self.instrument.write(f"SOURce:VOLTage:CURRent:LIMit {self.current_limit}")
            time.sleep(0.1)
            self.instrument.write("SOURce:VOLTage:RANGe:CURRent:AUTO ON")
            time.sleep(0.1)
            self.instrument.write("SOURce:VOLTage:MEASure:PRIMary VOLTage")
            time.sleep(0.1)
            self.instrument.write("SOURce:VOLTage:MEASure:SECondary CURRent")
            time.sleep(0.1)
            self.instrument.write("OUTPut:STATe ON")
            time.sleep(1)
            
            # Start the sweep using adaptive stepping.
            voltage = self.min_voltage
            base_step = 0.25  # Standard base step.
            min_step = 0.01
            max_step = base_step * 2
            step = base_step
            previous_current = None
            
            while self._running and voltage <= self.max_voltage:
                # Check and honor the pause flag.
                while self._paused and self._running:
                    time.sleep(0.1)
                if not self._running:
                    break
                
                # Enable/disable HV state based on the voltage magnitude.
                if abs(voltage) < 42.0:
                    self.instrument.write("SYSTem:MODE:HV:STATe 0")
                else:
                    self.instrument.write("SYSTem:MODE:HV:STATe 1")
                
                # Set the voltage output on the instrument.
                self.instrument.write(f"SOURce:VOLTage:FIXed {voltage}")
                time.sleep(0.1)  # Allow time for voltage to settle
                
                # Query the instrument for current measurements.
                meas_voltage = float(self.instrument.query("MEASure:PRIMary:LIVEdata?"))
                meas_current = float(self.instrument.query("MEASure:SECondary:LIVEdata?"))
                self.new_data.emit(meas_voltage, meas_current)
                
                # Calculate the adaptive step size based on the change in current.
                if previous_current is not None:
                    delta = abs(meas_current - previous_current)
                    step = base_step * (self.sensitivity / (self.sensitivity + delta))
                    step = max(min_step, min(step, max_step))
                previous_current = meas_current
                
                voltage += step
                if voltage > self.max_voltage:
                    voltage = self.max_voltage
                time.sleep(0.05)
                
            # Sweep completed; turn off output.
            self.instrument.write("OUTPut:STATe OFF")
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))
            try:
                self.instrument.write("OUTPut:STATe OFF")
            except Exception:
                pass
            self.finished.emit()

    def pause(self):
        """Pause the sweep."""
        self._paused = True

    def resume(self):
        """Resume the sweep."""
        self._paused = False

    def stop(self):
        """Stop the sweep."""
        self._running = False

# =============================================================================
# MplCanvas: Matplotlib canvas embedded in a PyQt widget.
# =============================================================================
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        """
        Initialize the Matplotlib figure and axes.
        """
        fig = Figure(figsize=(5, 4), dpi=200, constrained_layout=True)
        self.ax = fig.add_subplot(111)
        self.ax.grid(True)
        fig.set_constrained_layout_pads(w_pad=0.2, h_pad=0.2, wspace=0.2, hspace=0.3)
        super().__init__(fig)

# =============================================================================
# MainWindow: The main GUI window containing all controls and the plot.
# =============================================================================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IV Sweep Controller")
        self.resize(1920, 1080)
        
        # Instrument and threading variables.
        self.instrument = None
        self.rm = None
        self.worker = None
        self.thread = None
        
        # -----------------------------
        # Create main layout and widgets
        # -----------------------------
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Create a grid layout for parameter input controls.
        controls_layout = QtWidgets.QGridLayout()
        # Create a horizontal layout for primary control buttons.
        buttons_layout = QtWidgets.QHBoxLayout()
        
        # Create and configure QLineEdit widgets for user input.
        self.current_limit_edit = QtWidgets.QLineEdit()
        self.current_limit_edit.setPlaceholderText("Current Compliance (A)")
        current_validator = QtGui.QDoubleValidator(0.0, 0.1, 2, self)
        current_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.current_limit_edit.setValidator(current_validator)
        
        self.min_voltage_edit = QtWidgets.QLineEdit()
        self.min_voltage_edit.setPlaceholderText("Min Voltage (V)")
        min_voltage_validator = QtGui.QDoubleValidator(-200.0, 200.0, 2)
        min_voltage_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.min_voltage_edit.setValidator(min_voltage_validator)
        
        self.max_voltage_edit = QtWidgets.QLineEdit()
        self.max_voltage_edit.setPlaceholderText("Max Voltage (V)")
        max_voltage_validator = QtGui.QDoubleValidator(-200.0, 200.0, 2)
        max_voltage_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.max_voltage_edit.setValidator(max_voltage_validator)
        
        self.sensitivity_edit = QtWidgets.QLineEdit()
        self.sensitivity_edit.setPlaceholderText("Adaptive Sensitivity")
        self.sensitivity_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"^\d+(\.\d+)?$")))
        
        # Add the input widgets and their labels to the grid layout.
        controls_layout.addWidget(QtWidgets.QLabel("Current Compliance (A):"), 0, 0)
        controls_layout.addWidget(self.current_limit_edit, 0, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Min Voltage (V):"), 1, 0)
        controls_layout.addWidget(self.min_voltage_edit, 1, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Max Voltage (V):"), 2, 0)
        controls_layout.addWidget(self.max_voltage_edit, 2, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Adaptive Sensitivity:"), 3, 0)
        controls_layout.addWidget(self.sensitivity_edit, 3, 1)
        
        # Create primary control buttons.
        self.connect_button = QtWidgets.QPushButton("Connect/Initialize")
        self.start_button = QtWidgets.QPushButton("Start")
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.toggle_scale_button = QtWidgets.QPushButton("Toggle Scale (Linear/Log)")
        
        # Add the buttons to the horizontal layout.
        buttons_layout.addWidget(self.connect_button)
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.toggle_scale_button)
        
        # Create a status indicator (a small colored frame) to show the probe state.
        self.status_indicator = QtWidgets.QFrame()
        self.status_indicator.setFixedSize(20, 20)
        self.set_status("offline")
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.addWidget(QtWidgets.QLabel("Probe Status:"))
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        
        # Create additional buttons for saving and loading data.
        self.save_data_button = QtWidgets.QPushButton("Save Data to CSV")
        self.save_plot_button = QtWidgets.QPushButton("Save Plot to PNG")
        self.upload_csv_button = QtWidgets.QPushButton("Upload CSV")
        extra_buttons_layout = QtWidgets.QHBoxLayout()
        extra_buttons_layout.addWidget(self.save_data_button)
        extra_buttons_layout.addWidget(self.save_plot_button)
        extra_buttons_layout.addWidget(self.upload_csv_button)
        
        # Add the analysis window button.
        self.analysis_window = None
        self.open_analysis_button = QtWidgets.QPushButton("Open Analysis Window")
        extra_buttons_layout.addWidget(self.open_analysis_button)
        self.open_analysis_button.clicked.connect(self.open_analysis_window)
        
        # Add the control layouts to the main layout.
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(status_layout)
        main_layout.addLayout(extra_buttons_layout)
        
        # -----------------------------
        # Create the Matplotlib canvas and toolbar.
        # -----------------------------
        self.canvas = MplCanvas(self)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.toolbar)
        
        # Set up the initial plot labels and title.
        self.canvas.ax.set_xlabel("Voltage (V)")
        self.canvas.ax.set_ylabel("Current (A)")
        self.canvas.ax.set_title("IV Curve")
        # Initialize an empty line plot.
        self.line, = self.canvas.ax.plot([], [], 'b-o')
        # Lists to store sweep data.
        self.voltages = []
        self.currents = []
        
        # -----------------------------
        # Connect button signals to their corresponding slots.
        # -----------------------------
        self.connect_button.clicked.connect(self.connect_instrument)
        self.start_button.clicked.connect(self.start_sweep)
        self.pause_button.clicked.connect(self.pause_resume)
        self.stop_button.clicked.connect(self.stop_sweep)
        self.toggle_scale_button.clicked.connect(self.toggle_scale)
        self.save_data_button.clicked.connect(self.save_data_to_csv)
        self.save_plot_button.clicked.connect(self.save_plot_to_png)
        self.upload_csv_button.clicked.connect(self.upload_csv)
        
        # Track sweep status.
        self.sweep_running = False
        self.sweep_paused = False

    def set_status(self, state):
        """
        Set the probe status indicator color.
        """
        colors = {"ready": "green", "running": "red", "paused": "yellow", "offline": "grey"}
        color = colors.get(state, "grey")
        self.status_indicator.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        
    def connect_instrument(self):
        """
        Attempt to connect to the instrument via pyvisa.
        """
        try:
            self.rm = pyvisa.ResourceManager()
            # Update the VISA address as needed.
            self.instrument = self.rm.open_resource('ASRL3::INSTR')
            self.instrument.timeout = 10000
            self.instrument.write_termination = '\n'
            self.instrument.read_termination = '\n'
            self.set_status("ready")
            QtWidgets.QMessageBox.information(self, "Success", "Instrument connected and initialized.")
        except Exception as e:
            self.set_status("offline")
            QtWidgets.QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")
        
    def start_sweep(self):
        """
        Read the user parameters, reset any previous data, and start the IV sweep
        in a new thread using SweepWorker.
        """
        if not self.instrument:
            QtWidgets.QMessageBox.warning(self, "Error", "Instrument not connected!")
            return
        
        try:
            current_limit = float(self.current_limit_edit.text())
            min_voltage = float(self.min_voltage_edit.text())
            max_voltage = float(self.max_voltage_edit.text())
            sensitivity = float(self.sensitivity_edit.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter valid numeric parameters.")
            return
        
        if min_voltage >= max_voltage:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Min Voltage must be less than Max Voltage.")
            return
        
        # Clear previous data and reset the plot.
        self.voltages = []
        self.currents = []
        self.line.set_data(self.voltages, self.currents)
        self.canvas.ax.relim()
        self.canvas.ax.autoscale_view()
        self.canvas.draw()
        
        # Create and start the sweep thread.
        self.thread = QtCore.QThread()
        self.worker = SweepWorker(self.instrument, current_limit, min_voltage, max_voltage, sensitivity)
        self.worker.moveToThread(self.thread)
        self.worker.new_data.connect(self.update_plot)
        self.worker.finished.connect(self.sweep_finished)
        self.worker.error.connect(self.handle_error)
        self.thread.started.connect(self.worker.run)
        
        self.thread.start()
        self.sweep_running = True
        self.sweep_paused = False
        self.pause_button.setText("Pause")
        self.set_status("running")
        
    def refresh_plot(self):
        """
        Update the plot line data.
        """
        plot_currents = np.abs(self.currents) if self.canvas.ax.get_yscale() == "log" else self.currents
        self.line.set_data(self.voltages, plot_currents)
        self.canvas.ax.relim()
        self.canvas.ax.autoscale_view()
        self.canvas.draw()

    def update_plot(self, voltage, current):
        """
        Append new voltage/current data and update the plot.
        """
        self.voltages.append(voltage)
        self.currents.append(current)
        self.refresh_plot()
        if self.analysis_window is not None:
            self.analysis_window.voltages = self.voltages
            self.analysis_window.currents = self.currents

    def pause_resume(self):
        """
        Toggle the pause/resume state of the sweep.
        """
        if not self.worker:
            return
        if self.sweep_paused:
            self.worker.resume()
            self.sweep_paused = False
            self.pause_button.setText("Pause")
            self.set_status("running")
        else:
            self.worker.pause()
            self.sweep_paused = True
            self.pause_button.setText("Resume")
            self.set_status("paused")
        
    def stop_sweep(self):
        """
        Stop the sweep and safely disconnect the instrument.
        """
        if self.worker:
            self.worker.stop()
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        if self.instrument:
            try:
                self.instrument.write("*RST")
                self.instrument.write("OUTPut:STATe OFF")
                self.instrument.close()
            except Exception as e:
                print(f"Error during disconnect: {e}")
            self.instrument = None
        self.set_status("offline")
        QtWidgets.QMessageBox.information(self, "Sweep Cancelled", "Sweep cancelled.")
        self.sweep_running = False
        
    def sweep_finished(self):
        """
        Called when the sweep finishes normally.
        """
        self.thread.quit()
        self.thread.wait()
        self.set_status("ready")
        QtWidgets.QMessageBox.information(self, "Sweep Completed", "Sweep finished successfully.")
        
    def handle_error(self, error_msg):
        """
        Display an error message and stop the sweep.
        """
        QtWidgets.QMessageBox.critical(self, "Sweep Error", error_msg)
        self.stop_sweep()
        
    def toggle_scale(self):
        """
        Toggle the y-axis scale between linear and logarithmic.
        """
        if not self.voltages or not self.currents:
            QtWidgets.QMessageBox.warning(self, "No Data", "No data available to toggle scale.")
            return
        current_scale = self.canvas.ax.get_yscale()
        self.canvas.ax.set_yscale("log" if current_scale == "linear" else "linear")
        self.refresh_plot()

    def save_data_to_csv(self):
        """
        Save the current voltage/current data to a CSV file.
        """
        if not self.voltages or not self.currents:
            QtWidgets.QMessageBox.warning(self, "No Data", "No data available to save.")
            return
        df = pd.DataFrame({"Voltage (V)": self.voltages, "Current (A)": self.currents})
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv)")
        if filename:
            try:
                df.to_csv(filename, index=False)
                QtWidgets.QMessageBox.information(self, "Saved", f"Data saved to {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Save Error", str(e))
                
    def save_plot_to_png(self):
        """
        Save the current plot to a PNG image file.
        """
        if not self.voltages or not self.currents:
            QtWidgets.QMessageBox.warning(self, "No Data", "No data available to save plot.")
            return
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png)")
        if filename:
            try:
                self.canvas.figure.savefig(filename)
                QtWidgets.QMessageBox.information(self, "Saved", f"Plot saved to {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Save Error", str(e))
                
    def upload_csv(self):
        """
        Load voltage/current data from a CSV file and update the plot.
        """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if filename:
            try:
                df = pd.read_csv(filename)
                if "Voltage (V)" in df.columns and "Current (A)" in df.columns:
                    self.voltages = df["Voltage (V)"].tolist()
                    self.currents = df["Current (A)"].tolist()
                    self.line.set_data(self.voltages, self.currents)
                    self.canvas.ax.relim()
                    self.canvas.ax.autoscale_view()
                    self.canvas.draw()
                    QtWidgets.QMessageBox.information(self, "File Loaded", "CSV data loaded successfully.")
                else:
                    QtWidgets.QMessageBox.warning(self, "File Error", "CSV does not contain required columns 'Voltage (V)' and 'Current (A)'.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "File Error", str(e))

    def open_analysis_window(self):
        if not self.voltages or not self.currents:
            QtWidgets.QMessageBox.warning(
                self, "No Data",
                "No data available for analysis. Please run a sweep or upload CSV data first."
            )
            return
        # import the new launcher from your refactored GUI module
        from GUIFinalRefactored import launch_GUIFinal
        measured_data = np.column_stack((self.voltages, self.currents))
        proc  = Process(target=launch_GUIFinal, args=(measured_data,), daemon=True)
        proc.start()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    
