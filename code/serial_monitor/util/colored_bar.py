from tkinter import Canvas, Scale, IntVar, Entry
import tkinter as tk


def lerp(low, high, perc):
    return (high - low) * perc + low


def clamp(value, small, big):
    if value <= small:
        value = small
    if value >= big:
        value = big
    return value


SLIDER_WIDTH = 19  # slider width in px from left to centre


class ColoredBar(tk.Frame):
    RANGE = [0, 1000]

    def __init__(self, *args):
        super().__init__(*args)
        # current value
        self.canvas = Canvas(self, bd=1, relief="solid", width=98, height=15)
        self.canvas.pack(expand=True, fill="both")
        self.critical = 800

        self.slider = Scale(
            self, from_=0, to=1000, orient="horizontal", command=self.set_critical
        )
        self.slider.pack(expand=True, fill="both")

        self.entry = Entry(self, justify="center")
        self.entry.bind("<FocusOut>", self.set_critical_entry)
        self.entry.bind("<Return>", self.set_critical_entry)
        self.entry.pack(expand=True, fill="both")
        self.valid_range = self.RANGE

        tk.Button(self).pack()

    def set_range(self, valid_range):
        """valid range for raw and cutoff"""
        self.valid_range = valid_range

    def set_critical_entry(self, *args):
        value = self.entry.get()
        try:
            value = int(value)
            value = clamp(value, *self.valid_range)
        except:
            value = self.critical
            raise
        self.set_critical(value)

    def set_critical(self, value):
        self.critical = int(value)
        # update entries text
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(value))
        self.slider.set(value)
        # debug only:
        # self.set_value(value)

    def set_value(self, value):
        """
        sets the raw value
        """
        value = float(value)
        self.canvas.delete(tk.ALL)
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        perc = float(value) / 1000.0
        x_right = lerp(SLIDER_WIDTH, width - SLIDER_WIDTH, perc)

        text_anchor = "w" if value < 500 else "e"

        if value < self.critical:
            fill = "yellow"
        else:
            fill = "green"

        self.canvas.create_rectangle(SLIDER_WIDTH, 5, x_right, height - 5, fill=fill)
        self.canvas.create_text(
            x_right + 5, height / 2, text=str(int(value)), anchor=text_anchor
        )


if __name__ == "__main__":
    root = tk.Tk()

    cb = ColoredBar(root)
    cb.grid(row=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.mainloop()
