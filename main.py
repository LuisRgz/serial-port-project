import tkinter as tk
from collections import deque
from tkinter import NORMAL, DISABLED

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import serial
import tk_tools
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ser = serial.Serial("/dev/cu.usbserial-110", 9600)

action1 = b'A'
action2 = b'B'
action3 = b'C'
ledOn = b'T'
ledOff = b'O'
start = b'L'
end = b'M'


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
    def __init__(self, parent, axle_info=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        if axle_info is None:
            axle_info = [{"x": 100, "y": 100}]
        self.plot_size = len(axle_info)
        self.number_options = dict()
        self.selected_plot = 0
        self.ax_data = list()
        self.axis = list()
        for i in range(0, self.plot_size):
            self.number_options[axle_info[i]["title"]] = i
            self.ax_data.append(deque([0.0] * axle_info[i]["x"]))
            self.axis.append(axle_info[i])

        plt.style.use('dark_background')

        # Config graph
        self.graph_frame = tk.Frame(self, bg="#151515")
        self._figure, self._ax = plt.subplots(1, 1)
        self._figure_canvas = FigureCanvasTkAgg(
            self._figure, master=self.graph_frame
        )
        self.graph_frame.grid_columnconfigure(0, weight=1, uniform="fig")
        self._figure_canvas.get_tk_widget().grid(
            row=0, column=0, padx=(10, 10), pady=(10, 10),
            sticky="nsew"
        )

        # Config gauge
        self.gauges_frame = tk.Frame(self, bg="#151515")
        self.gauges = list()
        for i in range(0, self.plot_size):
            self.gauges.append(
                tk_tools.Gauge(
                    self.gauges_frame, max_value=self.axis[i]["y"],
                    divisions=10,
                    width=int(600), height=200,
                    unit=self.axis[i]["symbol"],
                    red_low=0, yellow_low=0, yellow=1000, red=1000,
                    bg="#151515"
                )
            )
        self.gauges[0].pack(
            side="left",
            fill="y", expand=True
        )

        # Configure controls
        self.frame_buttons = tk.Frame(self, bg="#151515")

        self.led = tk_tools.Led(self.frame_buttons, size=50)
        self.led.to_grey()

        self.btn_init = tk.Button(
            self.frame_buttons, bg="#7401DF", fg="#000000",
            activebackground="#8258FA", font=('Courier', 16),
            text="Iniciar", command=self.start_communication
        )

        self.led_check = tk_tools.SmartCheckbutton(
            self.frame_buttons, text="Encender LED",
            command=self.activate_led
        )

        value = tk.StringVar()
        value.set(self.axis[0]["title"])
        self.plot_options = tk.OptionMenu(
            self.frame_buttons, value,
            *list(map(lambda x: x["title"], self.axis)),
            command=self.select_plot
        )
        self.plot_options.configure(width=10)

        # show controls
        self.plot_options.pack(
            side="left", padx=(100, 100), pady=(50, 50),
            fill="y", expand=True
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

        # show frames
        self.graph_frame.pack(fill="x")
        self.gauges_frame.pack(fill="x")
        self.frame_buttons.pack(fill="x")

        self._init_axles()

    def select_plot(self, value):
        # hide gauges
        for i in range(0, self.plot_size):
            self.gauges[i].pack_forget()
        # select graph
        self.selected_plot = self.number_options[value]
        self._init_axles()
        self.gauges[self.number_options[value]].pack(
            side="left",
            fill="y", expand=True
        )

    # add graph data
    def add(self, data):
        assert (len(data) >= self.plot_size)
        for i in range(0, self.plot_size):
            add_to_buffer(self.ax_data[i], self.axis[i]["x"], data[i])

    def process_action(self, action):
        if action == action1:
            self.led.to_green(True)
        elif action == action2:
            self.led.to_red(True)
        elif action == action3:
            self.led.to_yellow(True)

    # update plot
    def update(self, frame_num, a):
        try:
            # read Serial data
            line = ser.readline()
            data = line.split()
            if len(data) >= self.plot_size + 1:
                self.process_action(data[0])
                # fill graph data
                analog_data = data[1:]
                for i in range(0, self.plot_size):
                    analog_data[i] = float(analog_data[i])
                # fill gauge
                self.gauges[self.selected_plot].set_value(analog_data[self.selected_plot])
                # fill graph data
                self.add(analog_data)
                a.set_data(range(self.axis[self.selected_plot]["x"]), self.ax_data[self.selected_plot])
        except KeyboardInterrupt:
            print('exiting')

        return a,

    def _init_axles(self):
        init_axis(self._ax, self.axis[self.selected_plot])

    def _init_animation(self):
        # init serial communication
        ser.write(start)
        # Configure graph line
        line = self._ax.plot([], [], color='#80FF00')[0]
        # Configure animation
        self._anim1 = animation.FuncAnimation(
            self._figure, self.update, interval=0.1, fargs=(line,)
        )
        self.btn_init.configure(text="Detener")
        self.plot_options.config(state=DISABLED)
        self._figure_canvas.draw()

    def start_communication(self):
        if self._anim1 is None:
            self._init_animation()
        else:
            if self.btn_init["text"] == "Iniciar":
                # init serial communication
                ser.write(start)
                self._anim1.event_source.start()
                self.btn_init.configure(text="Detener")
                self.plot_options.config(state=DISABLED)
            else:
                # stop serial communication
                ser.write(end)
                self._anim1.event_source.stop()
                self.btn_init.configure(text="Iniciar")
                self.plot_options.config(state=NORMAL)

    def activate_led(self):
        if self.led_check.get():
            ser.write(ledOn)
        else:
            ser.write(ledOff)


def close_window():
    # Destroys all widgets and closes the main loop
    ser.write(end)
    ser.close()
    root.destroy()
    # Close port
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
            {"x": 100, "y": 1050, "title": "Potenciometro", "x_title": "Tiempo", "y_title": "Amplitud", "symbol": ""},
            {"x": 100, "y": 1050, "title": "Fotoresistencia", "x_title": "Tiempo", "y_title": "Amplitud", "symbol": ""},
            {"x": 100, "y": 1050, "title": "Eje x", "x_title": "Tiempo", "y_title": "Amplitud", "symbol": ""},
            {"x": 100, "y": 1050, "title": "Eje y", "x_title": "Tiempo", "y_title": "Amplitud", "symbol": ""},
            {"x": 100, "y": 1050, "title": "Reflexión", "x_title": "Tiempo", "y_title": "Amplitud", "symbol": ""},

        ]
    ).pack(side="top", fill="both", expand=True)
    root.mainloop()
