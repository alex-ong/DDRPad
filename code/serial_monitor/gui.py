import serial_prog
import tkinter as tk
from tkinter import Tk, Label, Button, StringVar, OptionMenu, Entry, IntVar
import tkinter.font as tkFont
from util.colored_bar import ColoredBar


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


def get_numbers(string):
    """
    convert from 'sens: 123, 123, 123, 123' to [123,123,123,123]
    """
    idx = string.index(":")
    text = string[idx + 1 :]
    return [int(i) for i in text.split(",")]


class SerialGUI:
    def __init__(self, master):
        self.master = master
        master.title("DDR Pad Sensitivity")

        self.label = Label(master, text="DDRPad Sensitivity adjustment!")
        self.label.grid(row=0, sticky="nsew", columnspan=5)

        self.connection = None

        # port frame
        frame = tk.Frame(master)
        frame.grid(row=1, column=0, sticky="nsew", columnspan=5)
        self.setup_port_frame(frame)

        # sensitivity frame
        frame = tk.Frame(master)
        frame.grid(row=2, column=0, rowspan=5, columnspan=5, sticky="nsew")
        self.setup_sensitivity(frame)

        # debounce frame
        frame = tk.Frame(master)
        frame.grid(row=8, column=0, rowspan=5, columnspan=5, sticky="nsew")
        self.setup_debounce(frame)

        # bottom label
        label = Label(
            master,
            text="Disclaimer: Pad slows down while debugging to 100hz~ ©2021 XeaL.",
        )
        label.grid(row=13, column=0, columnspan=5, sticky="nsew")

        for row in range(14):
            self.master.grid_rowconfigure(row, weight=1)

        for col in range(5):
            self.master.grid_rowconfigure(col, weight=1)

    def setup_sensitivity(self, frame):
        Label(frame, text="🡄").grid(row=0, column=1, sticky="nsew")
        Label(frame, text="🡇").grid(row=0, column=2, sticky="nsew")
        Label(frame, text="🡅").grid(row=0, column=3, sticky="nsew")
        Label(frame, text="🡆").grid(row=0, column=4, sticky="nsew")

        # left side labels

        # sensitivity
        Label(frame, text="Pad's reported sensitivity (0-1000)").grid(
            row=1, column=0, sticky="nsew"
        )
        Label(frame, text="Current pad sensor value (0-1000)").grid(
            row=2, column=0, sticky="nsew"
        )
        Label(frame, text="Target pad sensor value (drag)").grid(
            row=3, column=0, sticky="nsew"
        )
        Button(
            frame, text="Target pad sensor value (type)", command=self.auto_sensitivity
        ).grid(
            row=4,
            column=0,
            sticky="nsew",
        )

        self.sens_bars = []
        sens = serial_prog.get_sens()
        for i, sen in enumerate(sens):
            bar = ColoredBar(frame)
            bar.set_critical(sen)
            bar.grid(row=1, column=i + 1, sticky="nsew", rowspan=4)
            self.sens_bars.append(bar)

        self.write_sens_out = Button(
            frame,
            text="Write sensitivity to pad",
            command=self.on_write_sens_remote,
        )
        self.write_sens_out.grid(row=6, column=1, columnspan=4, sticky="nsew")
        self.write_sens_out["state"] = "disabled"

        for row in range(7):
            frame.grid_columnconfigure(row, weight=1)

        for col in range(5):
            frame.grid_columnconfigure(col, weight=1)

    def setup_debounce(self, frame):
        Label(frame, text="Debounce in microseconds (5000µs = 5ms)").grid(
            row=0, columnspan=5, sticky="nsew"
        )
        Label(frame, text="Firmware debounce").grid(row=1, column=0, sticky="nsew")
        Label(frame, text="Target  debounce").grid(row=2, column=0, sticky="nsew")
        self.debounce_label = []
        for i in range(4):
            label = Label(frame, text="(debounce in µs)")
            label.grid(row=1, column=i + 1, sticky="nsew")
            self.debounce_label.append(label)

        self.debounce_vars = []
        debounce = serial_prog.get_debounce()
        for index, item in enumerate(debounce):
            trigger_var = IntVar()
            trigger_var.set(item)
            topEntry = Entry(frame, textvariable=trigger_var, justify="center")
            topEntry.bind("<FocusOut>", self.change_debounce)
            topEntry.grid(row=2, column=index + 1, sticky="nsew")
            self.debounce_vars.append(trigger_var)

        self.write_debounce_out = Button(
            frame,
            text="Write debounce time to pad",
            command=self.on_write_debounce_remote,
        )
        self.write_debounce_out.grid(row=3, column=1, columnspan=4, sticky="nsew")
        self.write_debounce_out["state"] = "disabled"

        for row in range(4):
            frame.grid_columnconfigure(row, weight=1)

        for col in range(5):
            frame.grid_columnconfigure(col, weight=1)

    def setup_port_frame(self, frame):
        ports_avail = serial_prog.get_ports()
        if len(ports_avail) == 0:
            ports_avail = ["No ports available"]
        Label(frame, text="Choose a port:").grid(
            row=0, column=0, columnspan=2, sticky="nsew"
        )
        self.port_var = StringVar()
        default_port = serial_prog.get_saved_port()
        if default_port in ports_avail:
            self.port_var.set(default_port)
        else:
            self.port_var.set(ports_avail[0])

        self.port_select = OptionMenu(frame, self.port_var, *ports_avail)
        self.port_select.grid(row=0, column=2, columnspan=2, sticky="nsew")

        self.port_var.trace("w", self.on_change_port)

        self.connect_button = Button(frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=4, columnspan=2, sticky="nsew")

        # debug on and off
        self.debug_on = Button(frame, text="Start pad data", command=self.turn_debug_on)
        self.debug_on["state"] = "disable"
        self.debug_on.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.debug_off = Button(
            frame, text="Stop pad data", command=self.turn_debug_off
        )
        self.debug_off["state"] = "disable"
        self.debug_off.grid(row=1, column=3, columnspan=3, sticky="nsew")

        for row in range(2):
            frame.grid_columnconfigure(row, weight=1)

        for col in range(6):
            frame.grid_columnconfigure(col, weight=1)

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

    def on_write_debounce_remote(self):
        self.change_debounce()  # bug where you click this when a textbox is focused.
        self.connection.port_write_debounce()
        self.update()

    def auto_sensitivity(self):
        """
        Automatically set sensitivity,
        based on idle value
        """
        sens = [-50, -60, -60, -60]
        for index, sen in enumerate(self.sens_bars):
            if sen.raw_value > 0:  # connected
                new_value = sen.raw_value + sens[index]
                sen.set_critical(new_value)

    def on_write_sens_remote(self):
        # bug where defocus might not always work
        for sen in self.sens_bars:
            sen.set_critical_entry()
        sens = [sen.critical for sen in self.sens_bars]
        serial_prog.set_sens_config(sens)
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
        self.turn_debug_on()
        self.update()

    def disconnect(self):
        self.turn_debug_off()
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
                pins = get_numbers(item)
            if item.startswith("sens"):
                sens = get_numbers(item)
            if item.startswith("debounce"):
                debounce = get_numbers(item)

        if pins is not None:
            for i in range(len(pins)):
                self.sens_bars[i].set_value(pins[i])

        if sens is not None:
            for i in range(len(sens)):
                self.sens_bars[i].set_firmware_value(sens[i])

        if debounce is not None:
            for i in range(len(debounce)):
                self.debounce_label[i]["text"] = debounce[i]

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
