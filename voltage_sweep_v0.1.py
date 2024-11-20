import pyvisa
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def save_to_file():
    data = {'Voltage (V)': voltages, 'Current (A)': currents}
    df = pd.DataFrame(data)
    
    # Base filename
    base_filename = "voltage_current_data"
    file_extension = ".csv"
    counter = 1

    # Find an unused filename
    while os.path.exists(f"{base_filename}_{counter}{file_extension}"):
        counter += 1

    filename = f"{base_filename}_{counter}{file_extension}"

    # Save the data
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()

# VISA address of your SMU4201 in the ' '
instrument = rm.open_resource('ASRL3::INSTR')

# Set the timeout and termination characters
instrument.timeout = 10000  # Set timeout to 10 seconds
instrument.write_termination = '\n'
instrument.read_termination = '\n'

# Set up the sweep parameters
current_limit = 0.015       # Current Limit (A) 
start_voltage = -10         # Starting voltage
end_voltage = 10            # Ending voltage
step_voltage = 0.5          # Voltage step size

voltages_to_sweep = np.arange(start_voltage, end_voltage + step_voltage, step_voltage)

voltages = []                # List to store voltage values
currents = []                # List to store current measurements

# Initialize plot
plt.ion()  # Turn on interactive mode for real-time plotting
fig, ax = plt.subplots()
line, = ax.plot(voltages, currents, 'b-o')
ax.set_xlabel("Voltage (V)")
ax.set_ylabel("Current (A)")
ax.set_title("Voltage-Current (IV) Curve")

try:
    # Reset the instrument to default settings
    instrument.write("*RST")
    time.sleep(1)  # Allow time for the reset

    # Set the instrument to Source Voltage mode and configure for current measurement
    instrument.write("SOURce:FUNCtion:MODE VOLTage")
    time.sleep(0.25)

    # Set the maximum (compliance) current to 10mA
    instrument.write(f'SOURce:VOLTage:CURRent:LIMit {current_limit}')  # Limit current to 10mA
    time.sleep(0.25)

    # Enable current auto-ranging
    instrument.write("SOURce:VOLTage:RANGe:CURRent:AUTO ON")
    time.sleep(0.25)

    # Set primary measurement to voltage and secondary measurement to current
    instrument.write("SOURce:VOLTage:MEASure:PRIMary VOLTage")  # Primary: Voltage
    instrument.write("SOURce:VOLTage:MEASure:SECondary CURRent")  # Secondary: Current
    time.sleep(0.25)

    # Enable the output
    instrument.write("OUTPut:STATe ON")
    time.sleep(1)

    # Perform the voltage sweep
    for voltage in voltages_to_sweep:

        # Set the voltage
        instrument.write(f"SOURce:VOLTage:FIXed {voltage}")
        time.sleep(0.1)  # Small delay to allow the voltage to settle

        # Query the current measurement
        current = float(instrument.query("MEASure:SECondary:LIVEdata?"))

        # Print the data point
        print(f"Voltage: {voltage:.6g} V, Current: {current:.6g} A") # 6 sig-figs
        
        # Store the values
        voltages.append(voltage)
        currents.append(current)
        
        # Update plot
        line.set_xdata(voltages)
        line.set_ydata(currents)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.1)  # Pause to update the plot (plot updates every .1 seconds)

    # Display final plot
    plt.ioff()  # Turn off interactive mode
    plt.show()

    save_to_file()

finally:
    # Turn off the output and close the connection
    instrument.write("OUTPut:STATe OFF")
    instrument.close()
