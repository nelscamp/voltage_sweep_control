import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from itertools import count, cycle
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import scipy.special as special
from scipy.integrate import quad
import pandas as pd

###########################################################################################

#Russell Burns

###########################################################################################

m_i = 6.7e-26
#AN=18 #atomic number
e = 1.60217663 * 10**-19
m_e = 9.1093837e-31



###########################################################################################

class ImageLabel(tk.Label): #from my kaleido repository
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        self.next_frame()

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

###########################################################################################
imported_data = None

def launch_GUIFinal(data=None):
    global imported_data
    imported_data = data   # your voltage/current pairs

    root = tk.Tk()
    root.title("IV Curve GUI")

    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    GIF_PATH  = os.path.join(BASE_DIR, "starsmall.gif")

    lbl = ImageLabel(root)
    lbl.pack()
    lbl.load(GIF_PATH)

    ###########################################################################################
    voltage_frame = LabelFrame(root, text = "Voltage Range",bg="#ccef1b", font="Z003")
    voltage_frame.pack()
    voltage_frame.place(relx=.1,rely=.9,anchor=CENTER)

    t1 = Label(voltage_frame, text="Units of V",bg="#ccef1b", font=("Arial", 10))
    t1.pack()

    textBox1=Text(voltage_frame, height=1, width=5)
    textBox1.pack(side=tk.LEFT)

    t2 = Label(voltage_frame, text=" to ",bg="#ccef1b", font=("Arial", 12))
    t2.pack(side=tk.LEFT)

    textBox2=Text(voltage_frame, height=1, width=5)
    textBox2.pack(side=tk.LEFT)

    ###########################################################################################
    temp_frame = LabelFrame(root, text = "e- Temperature",bg="#1BCCEF", font="Z003")
    temp_frame.pack()
    temp_frame.place(relx=.3,rely=.9,anchor=CENTER)

    t3 = Label(temp_frame, text=" ",bg="#1BCCEF")
    t3.pack(side=tk.LEFT)

    textBox3=Text(temp_frame, height=1, width=5)
    textBox3.pack(side=tk.LEFT)

    t4 = Label(temp_frame, text=" ",bg="#1BCCEF")
    t4.pack(side=tk.LEFT)

    options = [ 
        "eV"
    ] 
    
    clicked = StringVar() 
    
    clicked.set( "eV" ) 
    
    drop_temp = OptionMenu(temp_frame , clicked , *options ) 
    drop_temp.pack(side=tk.LEFT) 

    ###########################################################################################

    density_frame = LabelFrame(root, text = "e- Density",bg="#ccef1b", font="Z003")
    density_frame.pack()
    density_frame.place(relx=.5,rely=.9,anchor=CENTER)

    t5 = Label(density_frame, text=" ",bg="#ccef1b")
    t5.pack(side=tk.LEFT)

    textBox4=Text(density_frame, height=1, width=5)
    textBox4.pack(side=tk.LEFT)

    t6 = Label(density_frame, text=" ",bg="#ccef1b")
    t6.pack(side=tk.LEFT)

    options = [ 
        "m^-3", 
    ] 
    
    clicked = StringVar() 
    
    clicked.set( "m^-3" ) 
    
    drop_temp = OptionMenu(density_frame, clicked , *options ) 
    drop_temp.pack(side=tk.LEFT) 

    ###########################################################################################

    probe_length_frame = LabelFrame(root, text = "Probe Length",bg="#1BCCEF", font="Z003")
    probe_length_frame.pack()
    probe_length_frame.place(relx=.7,rely=.925,anchor=CENTER)

    t7 = Label(probe_length_frame, text=" ",bg="#1BCCEF")
    t7.pack(side=tk.LEFT)

    textBox5=Text(probe_length_frame, height=1, width=5)
    textBox5.pack(side=tk.LEFT)

    t8 = Label(probe_length_frame, text=" ",bg="#1BCCEF")
    t8.pack(side=tk.LEFT)

    options = [ 
        "mm"
    ] 
    
    # datatype of menu text 
    clicked = StringVar() 
    
    # initial menu text 
    clicked.set( "mm" ) 
    
    # create Dropdown menu 
    drop_temp = OptionMenu(probe_length_frame, clicked , *options ) 
    drop_temp.pack(side=tk.LEFT) 

    ###########################################################################################

    probe_diameter_frame = LabelFrame(root, text = "Probe Diameter",bg="#1BCCEF", font="Z003")
    probe_diameter_frame.pack()
    probe_diameter_frame.place(relx=.7,rely=.85,anchor=CENTER)

    t9 = Label(probe_diameter_frame, text=" ",bg="#1BCCEF")
    t9.pack(side=tk.LEFT)

    textBox6=Text(probe_diameter_frame, height=1, width=5)
    textBox6.pack(side=tk.LEFT)

    t10 = Label(probe_diameter_frame, text=" ",bg="#1BCCEF")
    t10.pack(side=tk.LEFT)

    options = [ 
        "mm"
    ] 
    
    # datatype of menu text 
    clicked = StringVar() 
    
    # initial menu text 
    clicked.set( "mm" ) 
    
    # create Dropdown menu 
    drop_temp = OptionMenu(probe_diameter_frame, clicked , *options ) 
    drop_temp.pack(side=tk.LEFT) 

    ###########################################################################################

    floating_potential_frame = LabelFrame(root, text = "Floating Potential",bg="#1BCCEF", font="Z003")
    floating_potential_frame.pack()
    floating_potential_frame.place(relx=.9,rely=.9,anchor=CENTER)

    t13 = Label(floating_potential_frame, text=" ",bg="#1BCCEF")
    t13.pack(side=tk.LEFT)

    textBox7=Text(floating_potential_frame, height=1, width=5)
    textBox7.pack(side=tk.LEFT)

    t14 = Label(floating_potential_frame, text=" ",bg="#1BCCEF")
    t14.pack(side=tk.LEFT)

    options = [ 
        "V"
    ] 
    
    # datatype of menu text 
    clicked = StringVar() 
    
    # initial menu text 
    clicked.set( "V" ) 
    
    # create Dropdown menu 
    drop_temp = OptionMenu(floating_potential_frame, clicked , *options ) 
    drop_temp.pack(side=tk.LEFT) 

    ###########################################################################################

    t11 = Label(root, text="BRLPy",bg="#ef1bcc", font=("Arial Bold", 25))
    t11.pack()
    t11.place(relx=.5,rely=.05,anchor=CENTER)

    t12 = Label(root, text="Russell Burns '25 Honors EPAD Project",bg="#ef1bcc", font=("Arial", 15))
    t12.pack()
    t12.place(relx=.5,rely=.1,anchor=CENTER)

    def exitApp():
        root.destroy()

    exitButton = Button(root, command = exitApp, text="Exit", bg ='red', highlightcolor="pink")
    exitButton.pack(side=TOP)

    ###########################################################################################
    fig = Figure(figsize=(5.5, 5), dpi=100)

    global plot_frame
    plot_frame = None
    canvas = None
    toolbar = None
    
    global log_view_enabled
    log_view_enabled = False  

    def toggle_log_view(): 
        global log_view_enabled 
        log_view_enabled = not log_view_enabled
        plot()

    def plot():
        global plot_frame, canvas, toolbar 
        if plot_frame is None:
            plot_frame = tk.Frame(root)
            plot_frame.pack()
            plot_frame.place(relx=.5,rely=.45,anchor=CENTER)

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.get_tk_widget().pack()

            toolbar = NavigationToolbar2Tk(canvas, plot_frame)
            toolbar.update()
        fig.clear()

        v1_str = textBox1.get(1.0, "end-1c")
        v2_str = textBox2.get(1.0, "end-1c")
        T_ev_str = textBox3.get(1.0, "end-1c")
        n_e_str = textBox4.get(1.0, "end-1c")
        L_probe_str = textBox5.get(1.0, "end-1c")
        D_probe_str = textBox6.get(1.0, "end-1c")
        floating_potential_str = textBox7.get(1.0, "end-1c")
        

        try:
            v1 = float(v1_str)
            v2 = float(v2_str)
            T_ev = float(T_ev_str)
            n_e = float(n_e_str)
            L = float(L_probe_str)
            R = float(D_probe_str)
            V_f = float(floating_potential_str)
        except ValueError:
            print("Error: Input values must be numbers.")
            return
        
        #R=0.8 #in units of mm
        #L=12.7 #in units mm
        #n_e = 1e14
        #T_ev = 1
        #V_f=0

        S = 2*np.pi*R*L*1e-6 # probe area im m^2 (NOT mm)
        Debye=(np.sqrt((8.854*10**-12*T_ev)/(n_e*e)))
        Xi=(R*.001)/Debye #R in m
        print("Debye:", Debye*1000)

        V_P = V_f - (T_ev * np.log(.6*np.sqrt(2*np.pi*(m_e/m_i))))
        print("VP:", V_P)

        #ion current calculations
        #Tiv = .1   # ion temperature
        #Va=np.sqrt((958000000000**1.62e-19*T_ev)/(2*np.pi*AN))
        #Jr=1.6E-19*S*Va
        #print(Jr)
        #I_is=Jr * (n_e/1000000) * 100000000000000 * 0.001    
        n_i=n_e
        I_is = .6 * e * n_i * np.sqrt(T_ev*e/m_i) * S


        A=1.12+(1/((1/(.00034*Xi**6.87))-(1/(.145*np.log(Xi/110)))))
        B=.5+.008*Xi**1.5/np.exp(.18*Xi**.80)
        C=1.07+.95/Xi**1.01
        D=.05+1.54*Xi**.3/np.exp(1.135*Xi**.370)

        print("Xi",Xi)

        T_iv=.1
        def Ii(VB):
            if VB < V_f:
                return -(1 / ((1 / (A * (((V_f-VB)/T_iv))**B)**4 + 1 / (C * (((V_f-VB)/T_iv))**D)**4)**(1/4))) * I_is
            else:
                return 0
                #return -I_is * np.exp((V_P - VB) / T_iv)
            




        #electron current calculations

        def gamma(Xi, a, lambd, r):
            return (-a * (lambd**r) / special.gamma(r)) * (Xi**(r-1)) * np.exp(-lambd * Xi)

        def electron_param(x, Xi):
            base = (2 / np.sqrt(np.pi)) * np.sqrt(x) + special.erfcx(np.sqrt(x))
            return (((base-1) * np.exp(Xi * gamma(Xi, 4.17, .05307, 1.168) * x**gamma(Xi, -0.8655, .1507, 2.3)))+1)


        def coeft(x):
            result = (np.sqrt(np.pi) / 2) * special.erfcx(x) ##special function for exp(x**2) * erfcx(x), which is simply g(x) as defined in the paper
            return result


        def eta(y):
            return (1 / np.sqrt(np.pi)) * coeft(np.sqrt(y))

        def inner_integral(y_prime):
            result, _ = quad(eta, 0, y_prime)
            return result

        def outer_integral(y):
            def integrand(y_prime):
                inner = inner_integral(y_prime)
                if inner == 0:
                    return 0
                return 1 / np.sqrt(2 * inner)

            result, _ = quad(integrand, 0, y)
            return result

        outer_integral_vectorized = np.vectorize(outer_integral)

        def planar_electron(VB,Xi):
            return (1 + (outer_integral_vectorized(VB)/Xi))

        I_es = e * n_e * S * np.sqrt((T_ev*e)/(2*np.pi*m_e)) #chen

        def Ie(VB):
            if VB < V_P:
                    return I_es * np.exp(-(V_P - VB) / T_ev)
            else:
                if Xi >= 21.316:
                    return I_es * planar_electron((V_P - VB),Xi)
                elif Xi < 21.316:
                    return I_es * electron_param((VB - V_P),Xi) 



        VB_range = np.linspace(v1, v2, 100)
        global ideal_current 
        ideal_current = np.array([Ie(VB) for VB in VB_range]) + np.array([Ii(VB) for VB in VB_range])

        plot1 = fig.add_subplot(111)
        fig.suptitle("Simulated Langmuir IV Curves")
        fig.supxlabel("Probe Bias (V)")
        fig.supylabel("Current (A)")
        plot1.tick_params(axis='y', labelsize=8) 
        #plot1.plot(VB_range, ideal_current, color='blue', linestyle='-', linewidth=2, label = "Ideal Sweep")
        #plot1.plot(VB_range, np.array([Ie(VB) for VB in VB_range]), color='red', linestyle='-', linewidth=2, label = "Electron")
        #plot1.plot(VB_range, np.array([Ii(VB) for VB in VB_range]), color='green', linestyle='-', linewidth=2, label = "Ion")

        if log_view_enabled:
            plot1.plot(VB_range, np.abs(ideal_current), color='blue', linestyle='-', linewidth=2, label="Ideal Sweep")
        else:
            plot1.plot(VB_range, ideal_current, color='blue', linestyle='-', linewidth=2, label="Ideal Sweep")

        plot1.set_yscale('log' if log_view_enabled else 'linear')

        if imported_data is not None:
            y_data = np.abs(imported_data[:,1]) if log_view_enabled else imported_data[:,1]  ### ✅ Handle imported data too
            plot1.scatter(imported_data[:,0], y_data, color="red", label="Imported Data")
        
        plot1.grid(True)
        fig.legend(fontsize=8, loc="upper right")
        canvas.draw()

    log_button = tk.Button(root, text="Log View", height=2, width=10, command=toggle_log_view)
    log_button.pack()
    log_button.place(relx=.1, rely=.55, anchor=CENTER)

    plot_button = Button(root, command = plot, height = 2, width = 10, text="Plot")
    plot_button.pack()
    plot_button.place(relx=.9,rely=.75,anchor=CENTER)

    ### curve fit assessment
    def import_csv():
        global imported_data
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
        if file_path.endswith(".csv"):
            try:
                df = pd.read_csv(file_path)
                imported_data = df.to_numpy()
                plot()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
        if file_path.endswith(".txt"):
            try:
                imported_data = np.loadtxt(file_path, skiprows=22)
                plot()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load TXT: {str(e)}")
        if not file_path:
            return


    #def calculate_rmse():
        #interp_generated = np.interp(imported_data[:,0], ideal_current[:,0], ideal_current[:,1])
    # rmse = np.sqrt(np.mean((imported_data[:,1] - interp_generated) ** 2))
        #rmse_label.config(text=f"RMSE: {rmse:.6f}")


    btn_import = tk.Button(root, text="Import Data", height = 2, width = 10, command=import_csv)
    btn_import.pack()
    btn_import.place(relx=.1,rely=.75,anchor=CENTER)

    #btn_rmse = tk.Button(root, text="Calculate RMSE", command=calculate_rmse)
    #btn_rmse.pack()
    #btn_rmse.place(relx=.1,rely=.55,anchor=CENTER)

    #rmse_label = tk.Label(root, text="RMSE: ")
    #rmse_label.pack()
    #rmse_label.place(relx=.1,rely=.65,anchor=CENTER)

    root.mainloop()												
																							
if __name__ == "__main__":
    # so you can still run it standalone without passing data
    launch_GUIFinal(None)