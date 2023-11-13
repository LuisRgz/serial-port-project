import tkinter as tk
from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import serial
import tk_tools
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ser = serial.Serial("/dev/cu.usbserial-10", 9600)


def add_to_buffer(buf, max_len, val):
    if len(buf) < max_len:
        buf.append(val)
    else:
        buf.pop()
        buf.appendleft(val)


def init_axis(axis, data):
    axis.set_title(data["title"])
    axis.set_xlabel(data["x_title"])
    axis.set_ylabel(data["y_title"])
    axis.set_xlim(0, data["x"])
    axis.set_ylim(0, data["y"])


class AnalogSignals(tk.Frame):
    def __init__(self, parent, axle_sizes=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        if axle_sizes is None:
            axle_sizes = [{"x": 100, "y": 100}, {"x": 100, "y": 100}]
        self.parent = parent

        self.ax1_data = deque([0.0] * axle_sizes[0]["x"])
        self.ax2_data = deque([0.0] * axle_sizes[1]["x"])
        self.axis_1 = axle_sizes[0]
        self.axis_2 = axle_sizes[1]

        plt.style.use('dark_background')
        self.frame_graficas = tk.Frame(self, bg="#151515")
        self._figure_1, (self._ax1, self._ax2) = plt.subplots(1, 2)
        self._figure_1_canvas = FigureCanvasTkAgg(
            self._figure_1, master=self.frame_graficas
        )

        self.frame_graficas.grid_columnconfigure(0, weight=1, uniform="fig")

        self._figure_1_canvas.get_tk_widget().grid(
            row=0, column=0, padx=(10, 10), pady=(10, 10),
            sticky="nsew"
        )

        self.frame_gauges = tk.Frame(self, bg="#151515")

        self.gauge_1 = tk_tools.Gauge(
            self.frame_gauges, max_value=self.axis_1["y"],
            divisions=10,
            width=400, height=200,
            label='Temperatura', unit=self.axis_1["symbol"],
            red_low=0, yellow_low=0, yellow=1000, red=1000,
            bg="#151515"
        )
        self.gauge_1.pack(
            side="left", padx=(10, 10), pady=(10, 10),
            fill="y", expand=True
        )

        self.gauge_2 = tk_tools.Gauge(
            self.frame_gauges, max_value=self.axis_2["y"],
            divisions=10,
            width=400, height=200,
            label='Temperatura', unit=self.axis_2["symbol"],
            red_low=0, yellow_low=0, yellow=100, red=100,
            bg="#151515"
        )
        self.gauge_2.pack(
            side="left", padx=(10, 10), pady=(10, 10),
            fill="y", expand=True
        )

        self.frame_buttons = tk.Frame(self, bg="#151515")

        self.led = tk_tools.Led(self.frame_buttons, size=50)
        self.led.to_green()

        self.btn_init = tk.Button(
            self.frame_buttons, bg="#7401DF", fg="#000000",
            activebackground="#8258FA", font=('Courier', 16),
            text="Iniciar", command=self.start_communication
        )
        self.led_check = tk_tools.SmartCheckbutton(
            self.frame_buttons, text="Encender LED",
            command=self.activate_led
        )
        self.led.pack(
            side="left", padx=(100, 100), pady=(32, 32),
            fill="y", expand=True
        )
        self.btn_init.pack(
            side="left", padx=(100, 100), pady=(40, 40),
            fill="y", expand=True
        )
        self.led_check.pack(
            side="left", padx=(100, 100), pady=(50, 50),
            fill="y", expand=True
        )

        self._anim1 = None

        self.frame_graficas.pack(fill="x")
        self.frame_gauges.pack(fill="x")
        self.frame_buttons.pack(fill="x")
        self._init_axles()

    # add data
    def add(self, data):
        assert (len(data) == 2)
        add_to_buffer(self.ax1_data, self.axis_1["x"], data[0])
        add_to_buffer(self.ax2_data, self.axis_2["x"], data[1])

    # update plot
    def update(self, frameNum, a0, a1):
        try:
            line = ser.readline()
            data = line.split()
            if len(data) == 3:
                analog_0, analog_1, digital = data
                analog_0 = float(analog_0)
                analog_1 = float(analog_1)
                data = (analog_0, analog_1)
                self.gauge_1.set_value(analog_0)
                self.gauge_2.set_value(analog_1)
                if digital == b'A':
                    self.led.to_green(True)
                else:
                    self.led.to_grey()
                self.add(data)
                a0.set_data(range(self.axis_1["x"]), self.ax1_data)
                a1.set_data(range(self.axis_2["x"]), self.ax2_data)
        except KeyboardInterrupt:
            print('exiting')

        return a0,

    def _init_axles(self):
        init_axis(self._ax1, self.axis_1)
        init_axis(self._ax2, self.axis_2)

    def _init_animation(self):
        # init serial communication
        ser.write(b"L")
        lines = self._ax1.plot([], [], color='#80FF00')[0]
        lines2 = self._ax2.plot([], [], color='#80FF00')[0]
        self._anim1 = animation.FuncAnimation(
            self._figure_1, self.update, interval=10
            , fargs=(lines, lines2)
        )
        self.btn_init.configure(text="Detener")
        self._figure_1_canvas.draw()

    def start_communication(self):
        if self._anim1 is None:
            self._init_animation()
        else:
            if self.btn_init["text"] == "Iniciar":
                # init serial communication
                ser.write(b"L")
                self._anim1.event_source.start()
                self.btn_init.configure(text="Detener")
            else:
                # stop serial communication
                ser.write(b"M")
                self._anim1.event_source.stop()
                self.btn_init.configure(text="Iniciar")

    def activate_led(self):
        if self.led_check.get():
            ser.write(b"A")
        else:
            ser.write(b"B")


def close_window():
    # Destroys all widgets and closes the main loop
    root.destroy()
    # Close port
    ser.write(b"M")
    ser.close()
    print("Close Serial")
    # Ends the execution of the Python program
    exit()


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Señales Analógicas")
    root.protocol("WM_DELETE_WINDOW", close_window)
    AnalogSignals(
        root,
        [
            {"x": 100, "y": 100, "title": "Humedad", "x_title": "Tiempo", "y_title": "Porcentaje", "symbol": "%"},
            {"x": 100, "y": 40, "title": "Temperatura", "x_title": "Tiempo", "y_title": "Grados", "symbol": "º"}
        ]
    ).pack(side="top", fill="both", expand=True)
    root.mainloop()
