# Voltage Sweep Control
A control software interface for the SMU4201 source measure unit (SMU), specifically designed for controlling Langmuir probe voltage sweeps and generating IV (current-voltage) curves. These curves are essential for characterizing plasma properties, such as electron density, temperature, and plasma potential.

# Key Features
 - Voltage Sweep Control: Configure and control voltage parameters for Langmuir probe sweeps.
 - IV Curve Generation: Automatically capture and plot IV curves for plasma analysis.
 - Data Export: Export data in common formats for further processing and visualization.
 - User-Friendly Interface: An intuitive GUI built with CustomTkinter for ease of use.

# Technical Details
 - Language: Python
 - GUI Library: CustomTkinter
 - Supported Hardware: SMU4201 source measure unit (Note: may need to rewrite commands if using different source meters due to syntax differences.)

# Getting Started
## Prerequisites
Ensure you have the following installed:
 - Python 3.x
 - CustomTkinter
 - PyVISA (for SMU control)

To install the dependencies, run:

bash
copy code
pip install customtkinter pyvisa matplotlib numpy scipy

# Installation
Clone this repository:

git clone https://github.com/yourusername/SMU4201-langmuir-control.git
cd SMU4201-langmuir-control

# Running the Application
To start the control software, execute:

python main.py

# Usage
1. Setup Voltage Sweep: Input voltage range, step size, and any additional sweep parameters.
2. Start Sweep: Begin the Langmuir probe sweep to capture current data.
3. Generate IV Curve: The software will process the data and display an IV curve.
4. Data Export: Save the generated data for additional analysis if needed.

# File Structure
1. main.py: Main entry point for the software.
2. RevD.py: Configuration file for the SMU4201 device.
3. README.md: Project documentation.
4. LICENSE: Licensing information.
