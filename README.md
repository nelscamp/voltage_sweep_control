# Voltage Sweep Control
A control software interface for the **SMU4201 source measure unit (SMU)**, specifically designed for controlling **Langmuir probe voltage sweeps** and generating IV (current-voltage) curves. These curves are essential for characterizing plasma properties, such as electron density, temperature, and plasma potential.

# Key Features
 - **Voltage Sweep Control**: Configure and control voltage parameters for Langmuir probe sweeps.
 - **IV Curve Generation**: Automatically capture and plot IV curves for plasma analysis.
 - **Data Export**: Export data in common formats for further processing and visualization.

# Technical Details
 - **Language**: Python
 - **GUI Library**: PYQT (main.py) ; CustomTkinter (GUIFinalRefactored.py)
 - **Supported Hardware**: SMU4201 Source Measure Unit
*Note: may require rewriting commands if using different source meters due to syntax differences*

# Getting Started
# Prerequisites:
Install NI-VISA and NI 488.2 from NI.com

## Installation
Clone this repository:
```
git clone https://github.com/nelscamp/voltage_sweep_control.git
cd C:/path/to/folder/voltage_sweep_control
```

To install all dependencies, run:
```
# one-time setup
conda env create -f environment.yml      # creates the env from YAML
conda activate langmuir-gui-env          # activate it
```
or
```
pip install -r requirements.txt
```
# Running the Application
To start the control software, execute:
```
python main.py
```

# Usage
1. **Setup Voltage Sweep**: Input voltage range, step size, and any additional sweep parameters.
2. **Start Sweep**: Begin the Langmuir probe sweep to capture current data.
3. **Generate IV Curve**: The software will process the data and display an IV curve.
4. **Data Export**: Save the generated data for additional analysis if needed.

# File Structure
1. main.py: Main entry point for the software.
2. GUIFinalRefactored.py: Analysis window.
3. starsmall.gif: Necessary for analysis window.
4. requirements.txt: File of all dependencies used.
5. environment.yml: Source file of all dependencies used.
6. README.md: Project documentation.
7. LICENSE: Licensing information.
