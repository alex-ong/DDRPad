import serial_prog
import tkinter as tk
from tkinter import Tk, Label, Button, StringVar, OptionMenu, Entry, IntVar
import tkinter.font as tkFont


def clamp(value):
    if value <= 0:
        value = 0
    if value >= 1000:
        value = 1000
    return value

def clamp_long(value):
    if value <= 0:
        value = 0
    if value >= 100000:
        value = 100000
    return value

class SerialGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="Serial GUI for homepad!")
        self.label.pack()
        ports_avail = serial_prog.get_ports()
        if len(ports_avail) == 0:
            ports_avail = ["No ports available"]

        frame = tk.Frame(master)
        frame.pack()
        
        Label(frame, text="Choose a port:").grid(row=0,column=0,columnspan=2)
        self.port_var = StringVar()
        default_port = serial_prog.get_saved_port()
        if default_port in ports_avail:
            self.port_var.set(default_port)
        else:
            self.port_var.set(ports_avail[0])

        self.port_select = OptionMenu(frame, self.port_var, *ports_avail)
        self.port_select.grid(row=0,column=2,columnspan=2)

        self.port_var.trace("w", self.on_change_port)
                
        self.connect_button = Button(frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0,column=4,columnspan=2)
        
        #debug on and off
        self.debug_on = Button(
            frame, text="Start pad data", command=self.turn_debug_on
        )
        self.debug_on["state"] = "disable"
        self.debug_on.grid(row=1,column=0,columnspan=3)
        self.debug_off = Button(
            frame, text="Stop pad data", command=self.turn_debug_off
        )
        self.debug_off["state"] = "disable"
        self.debug_off.grid(row=1,column=3,columnspan=3)

        # sensor raw values
        Label(master, text="< v ^ >").pack()
        Label(master, text="Current pad values").pack()
        self.status_label = Label(master, text="status goes here")
        self.status_label.pack()
        # sensitivity
        Label(master, text="Pad's firmware sensitivities (0-1000)").pack()
        self.sens_label = Label(master, text="sens goes here")
        self.sens_label.pack()

        self.sens_vars = []
        sensitivities = serial_prog.get_sens()
        frame = tk.Frame(master)
        frame.pack()
        for index, item in enumerate(sensitivities):
            trigger_var = IntVar()
            trigger_var.set(item)
            topEntry = Entry(frame, textvariable=trigger_var)
            topEntry.bind("<FocusOut>", self.change_sens)
            topEntry.grid(row=0, column=index)
            self.sens_vars.append(trigger_var)

        self.write_sens_out = Button(
            master, text="Write sensitivity to pad", command=self.on_write_sens_remote
        )
        self.write_sens_out.pack()
        self.write_sens_out["state"] = "disabled"

        #debounce
        
        Label(master, text="Pad's firmware debounce (microseconds)").pack()
        self.debounce_label= Label(master, text="micros goes here")
        self.debounce_label.pack()
        
        self.debounce_vars = []
        debounce = serial_prog.get_debounce()
        frame = tk.Frame(master)
        frame.pack()
        for index, item in enumerate(debounce):
            trigger_var = IntVar()
            trigger_var.set(item)
            topEntry = Entry(frame, textvariable=trigger_var)
            topEntry.bind("<FocusOut>", self.change_debounce)
            topEntry.grid(row=0, column=index)
            self.debounce_vars.append(trigger_var)

        self.write_debounce_out = Button(
            master, text="Write debounce_time to pad", command=self.on_write_debounce_remote
        )
        self.write_debounce_out.pack()
        self.write_debounce_out["state"] = "disabled"
        
        

        self.connection = None

        
    def change_debounce(self, *args):
        values = serial_prog.get_debounce()
        for index, item in enumerate(self.debounce_vars):
            try:
                value = item.get()
                value = int(value)
                value = clamp_long(value)
                values[index] = value
                item.set(value)
            except:
                item.set(values[index])
                raise
        serial_prog.set_debounce_config(values)
        self.update()
        
    def change_sens(self, *args):
        values = serial_prog.get_sens()
        for index, item in enumerate(self.sens_vars):
            try:
                value = item.get()
                value = int(value)
                value = clamp(value)
                values[index] = value
                item.set(value)
            except:
                item.set(values[index])
                raise
        serial_prog.set_sens_config(values)
        self.update()

        
    def on_write_debounce_remote(self):
        self.change_debounce()  # bug where you click this when a textbox is focused.
        self.connection.port_write_debounce()
        self.update()
        
    def on_write_sens_remote(self):
        self.change_sens()  # bug where you click this when a textbox is focused.
        self.connection.port_write_sens()
        self.update()

    def update(self):
        self.master.update()

    def on_change_port(self, *args):
        value = self.port_var.get()
        if value != "No ports available":
            serial_prog.set_saved_port(self.port_var.get())

    def connect(self):
        self.connection = serial_prog.SerialPort()
        self.connection.connect()
        self.port_select.configure(state="disabled")
        self.connect_button.configure(command=self.disconnect)
        self.connect_button["text"] = "Disconnect"
        self.debug_on["state"] = "normal"
        self.debug_off["state"] = "disabled"
        self.write_sens_out["state"] = "normal"
        self.write_debounce_out["state"] = "normal"
        self.update()

    def disconnect(self):
        self.connection.disconnect()
        self.connection = None
        self.connect_button.configure(command=self.connect)
        self.connect_button["text"] = "Connect"
        self.debug_on["state"] = "disabled"
        self.debug_off["state"] = "disabled"
        self.write_sens_out["state"] = "disabled"
        self.write_debounce_out["state"] = "disabled"
        self.update()

    def turn_debug_off(self):
        self.connection.port_debug_off()
        self.debug_on["state"] = "normal"
        self.debug_off["state"] = "disabled"
        self.update()

    def turn_debug_on(self):
        self.connection.port_debug_on()
        self.debug_on["state"] = "disabled"
        self.debug_off["state"] = "normal"
        self.update()

    def read(self):
        data = self.connection.read()
        # get last two lines
        data = data[-2:]
        pins = None
        sens = None
        debounce = None
        for item in data:
            item = item.decode("utf-8").lower().strip()
            if item.startswith("pins"):
                pins = item
            if item.startswith("sens"):
                sens = item
            if item.startswith("debounce"):
                debounce = item
                
        if pins is not None:
            self.status_label["text"] = pins
        if sens is not None:
            self.sens_label["text"] = sens
        if debounce is not None:
            self.debounce_label["text"] = debounce
            
        self.update()


def task(my_gui):
    if my_gui.connection is not None:
        my_gui.read()
    root.after(1, lambda: task(my_gui))  # reschedule event in 2 seconds


root = tk.Tk()
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=15)
root.option_add("*Font", "TkDefaultFont")
my_gui = SerialGUI(root)
root.after(2000, lambda: task(my_gui))
root.mainloop()
