# Voltage Sweep Control
A control software interface for the **SMU4201 source measure unit (SMU)**, specifically designed for controlling **Langmuir probe voltage sweeps** and generating IV (current-voltage) curves. These curves are essential for characterizing plasma properties, such as electron density, temperature, and plasma potential.
## Key Features
 - **Voltage Sweep Control**: Configure and control voltage parameters for Langmuir probe sweeps.
 - **IV Curve Generation**: Automatically capture and plot IV curves for plasma analysis.
 - **Adaptive Sensitivity**: Adapative resolution when recording sweep data.
 - **Data Export**: Export data in common formats for further processing and visualization.
 - **Curve Fitting**: Perform curve fitting on IV curve data to extract plasma parameters.
## Technical Details
 - **Language**: Python
 - **GUI Library**: PYQT (main.py) ; CustomTkinter (GUIFinalRefactored.py)
 - **Supported Hardware**: SMU4201 Source Measure Unit

*Note: may require rewriting commands if using different source meters due to syntax differences*
## Getting Started
### Prerequisites:
Install NI-VISA and NI 488.2 from NI.com
### Installation
Clone this repository:
```
git clone https://github.com/nelscamp/voltage_sweep_control.git
cd C:/path/to/folder/voltage_sweep_control
```
**To install all dependencies, run:**
```
# one-time setup
conda env create -f environment.yml      # creates the env from YAML
conda activate langmuir-gui-env          # activate it
```
**or**
```
pip install -r requirements.txt
```
## Running the Application
To start the control software, execute:
```
python main.py
```
## Usage
**How to use:**
1. **Setup Voltage Sweep**: Input voltage range, current compliance, and adaptive sensitivity.
3. **Start Sweep**: Begin the Langmuir probe sweep to capture voltage-current data.
4. **Generate IV Curve**: The software will process the data and display an IV curve.
5. **Data Export**: Save the generated data for additional analysis if needed.

#### Adaptive Sensitivity Input:
Adaptive Sensitivity of **5.0 µA** means, if: <br/>
- **ΔI > 5.0 µA**, step size **decreases**,
- **ΔI ~ 5.0 µA**, step size stays around **base**,
- **ΔI < 5.0 µA**, step size **increases**.

*ΔI refers to change in current between successive points.*

| Resolution | Input Ranges |
| --- | ---: |
| Fast/Low Resolution | 10 µA + |
| Balanced | 3 µA - 8 µA |
| Slow/High Resolution | .1 µA - 2 µA |

**Step Sizes:** <br/>
**- Base Step Size:** _0.25V_ <br/>
**- Range:** _0.025V_ - _0.5V_
### Import Data for Analysis Window
1. Click the "Upload CSV" button (before opening analysis window).
2. Click on "Analysis Window" button.
### Analysis Window
1. Before clicking anything, input known parameters into the entry boxes.
2. Once all entry boxes are filled, click on the "plot" button.
3. Click "log" button to find floating potential (the local min).
4. Check print lines for the calculated parameters.

**Sample parameters for the supplied sample data (voltage sweep 23)** <br/>
Voltage Range: 40 to 70 (volts) <br/>
e- Temperature: .9 <br/>
e- Density: .65e14 <br/>
Probe Diameter: .8 <br/>
Probe Length: 12.7 <br/>
Floating Potential: 55.35 <br/>
## File Structure
1. main.py: Main entry point for the software.
2. GUIFinalRefactored.py: Analysis window.
3. starsmall.gif: Necessary for analysis window.
4. requirements.txt: File of all dependencies used.
5. environment.yml: Source file of all dependencies used.
6. README.md: Project documentation.
## Credits
**Nelson Campos and Russell Burns**
