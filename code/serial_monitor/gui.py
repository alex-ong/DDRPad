import serial_prog
import tkinter as tk
from tkinter import Tk, Label, Button, StringVar, OptionMenu


class SerialGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="Serial GUI for homepad!")
        self.label.pack()
        ports_avail = serial_prog.get_ports()
        if len(ports_avail) == 0:
            ports_avail = ["No ports available"]

        Label(master, text="Choose a port:").pack()
        self.port_var = StringVar()
        default_port = serial_prog.get_saved_port()
        if default_port in ports_avail:
            self.port_var.set(default_port)
        else:
            self.port_var.set(ports_avail[0])

        self.port_select = OptionMenu(master, self.port_var, *ports_avail)
        self.port_select.pack()

        self.port_var.trace("w", self.on_change_port)

        self.connect_button = Button(master, text="Connect", command=self.connect)
        self.connect_button.pack()

        self.status_label = Label(master, text="status goes here")
        self.status_label.pack()

        self.sens_label = Label(master, text="sens goes here")
        self.sens_label.pack()

        self.debug_label = Label(master, text="Debug is off")
        self.debug_label.pack()

        self.debug_on = Button(
            master, text="Start pad data", command=self.turn_debug_on
        )
        self.debug_on["state"] = "disable"
        self.debug_on.pack()
        self.debug_off = Button(
            master, text="Stop pad data", command=self.turn_debug_off
        )
        self.debug_off["state"] = "disable"
        self.debug_off.pack()

        self.connection = None

    def on_change_port(self, *args):
        value = self.port_var.get()
        if value != "No ports available":
            serial_prog.set_saved_port(self.port_var.get())

    def connect(self):
        self.connection = serial_prog.SerialPort()
        self.connection.connect()
        self.port_select.configure(state="disabled")
        self.connect_button.configure(command=self.disconnect)
        self.connect_button.configure(text="Disconnect")
        self.debug_on.configure(state="enabled")
        self.debug_off.configure(state="disabled")

    def disconnect(self):
        self.connection.disconnect()
        self.connection = None
        self.connect_button.configure(command=self.connect)
        self.connect_button.configure(text="Connect")
        self.debug_on.configure(state="disabled")
        self.debug_off.configure(state="disabled")

    def turn_debug_off(self):
        self.connection.port_debug_off()
        self.debug_on.configure(state="enabled")
        self.debug_off.configure(state="disabled")

    def turn_debug_on(self):
        self.connection.port_debug_on()
        self.debug_on.configure(state="disabled")
        self.debug_off.configure(state="enabled")

    def read(self):
        data = self.connection.read()
        # get last two lines
        data = data[-2:]
        pins = None
        sens = None
        for item in data:
            item = item.lower()
            if item.startswith("pins"):
                pins = item
            if items.startswith("sens"):
                sens = item
        if pins is not None:
            self.status_label.configure(text=pins)
        if sens is not None:
            self.sens_label.configure(text=sens)


def task(my_gui):
    if my_gui.connection is not None:
        my_gui.read()
    root.after(0, lambda: task(my_gui))  # reschedule event in 2 seconds


root = tk.Tk()
my_gui = SerialGUI(root)
root.after(2000, lambda: task(my_gui))
root.mainloop()
