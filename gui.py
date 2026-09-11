import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import time as _time
from io import StringIO
from collections import deque
from problems import producer_consumer, dining_philosopher, reader_writer
from utils.control import SimulationControl

# matplotlib integration
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# SPEED CONTROL (global)
# ============================================================
class SpeedControl:
    _speed = 1.0

    @classmethod
    def get(cls):
        return cls._speed

    @classmethod
    def set(cls, value):
        cls._speed = float(value)


# ============================================================
# PRODUCER-CONSUMER VISUALIZER
# ============================================================
class BufferVisualizer:
    """Animated buffer boxes + counters + progress bar (adaptive sizing)."""

    def __init__(self, parent, buffer_size, total_items):
        self.buffer_size = buffer_size
        self.total_items = total_items
        self.padding = 3

        MAX_CANVAS_WIDTH = 550
        available = MAX_CANVAS_WIDTH - self.padding * (buffer_size + 1)
        cell = available // buffer_size if buffer_size > 0 else 40
        self.cell_width = max(6, min(50, cell))
        self.cell_height = self.cell_width if self.cell_width < 30 else 42

        canvas_w = (self.cell_width + self.padding) * buffer_size + self.padding
        canvas_h = self.cell_height + 2 * self.padding

        self.canvas = tk.Canvas(
            parent, width=canvas_w, height=canvas_h,
            bg="white", highlightthickness=1, highlightbackground="#cccccc",
        )
        self.canvas.pack(pady=5)

        self.stats_label = tk.Label(
            parent, text="Produced: 0 | Consumed: 0 | In-flight: 0",
            font=("Courier New", 11, "bold"), fg="#333",
        )
        self.stats_label.pack(pady=2)

        self.buffer_label = tk.Label(
            parent, text=f"Buffer: 0 / {buffer_size}",
            font=("Courier New", 10), fg="#666",
        )
        self.buffer_label.pack(pady=2)

        self.progress = ttk.Progressbar(
            parent, length=canvas_w,
            maximum=total_items, mode="determinate",
        )
        self.progress.pack(pady=5)

        self.draw_buffer(0)

    def draw_buffer(self, items_in_buffer):
        self.canvas.delete("all")
        for i in range(self.buffer_size):
            x1 = self.padding + i * (self.cell_width + self.padding)
            y1 = self.padding
            x2 = x1 + self.cell_width
            y2 = y1 + self.cell_height
            filled = i < items_in_buffer
            color = "#4CAF50" if filled else "#EEEEEE"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#888")

            if self.cell_width >= 18:
                text_color = "white" if filled else "#666"
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(i + 1), fill=text_color,
                    font=("Courier New", max(6, self.cell_width // 4), "bold"),
                )

    def update(self, produced, consumed, items_in_buffer):
        self.draw_buffer(items_in_buffer)
        in_flight = produced - consumed
        self.stats_label.config(
            text=f"Produced: {produced} | Consumed: {consumed} | In-flight: {in_flight}"
        )
        self.buffer_label.config(text=f"Buffer: {items_in_buffer} / {self.buffer_size}")
        self.progress["value"] = consumed


# ============================================================
# THROUGHPUT GRAPH (matplotlib embedded)
# ============================================================
class ThroughputGraph:
    """Live line chart of two time series."""

    MAX_POINTS = 120

    def __init__(self, parent, ylabel="Items",
                 label1="Produced", color1="#4CAF50",
                 label2="Consumed", color2="#E91E63",
                 title="Throughput"):
        self.parent = parent
        self.start_time = _time.time()

        self.times = deque(maxlen=self.MAX_POINTS)
        self.s1 = deque(maxlen=self.MAX_POINTS)
        self.s2 = deque(maxlen=self.MAX_POINTS)
        self.label1 = label1
        self.label2 = label2

        self.fig = Figure(figsize=(5.5, 2.2), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Time (s)", fontsize=9)
        self.ax.set_ylabel(ylabel, fontsize=9)
        self.ax.set_title(title, fontsize=11, fontweight="bold")
        self.ax.tick_params(labelsize=8)
        self.ax.grid(True, alpha=0.3)

        (self.line1,) = self.ax.plot([], [], color=color1,
                                     linewidth=2, label=label1)
        (self.line2,) = self.ax.plot([], [], color=color2,
                                     linewidth=2, label=label2)
        self.ax.legend(loc="upper left", fontsize=8)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()

    def reset(self):
        self.start_time = _time.time()
        self.times.clear()
        self.s1.clear()
        self.s2.clear()
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def add_point(self, val1, val2):
        t = _time.time() - self.start_time
        self.times.append(t)
        self.s1.append(val1)
        self.s2.append(val2)
        self.line1.set_data(list(self.times), list(self.s1))
        self.line2.set_data(list(self.times), list(self.s2))
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()


# ============================================================
# DINING PHILOSOPHERS VISUALIZER
# ============================================================
class PhilosopherVisualizer:
    """Circle of philosophers with forks (green=held, gray=free)."""

    def __init__(self, parent, num_philosophers):
        self.n = num_philosophers
        self.size = 320   # fixed size — always fits on screen
        self.center = self.size // 2
        self.radius = self.size // 2 - 30

        self.canvas = tk.Canvas(
            parent, width=self.size, height=self.size,
            bg="white", highlightthickness=1, highlightbackground="#cccccc",
        )
        self.canvas.pack(pady=5)

        self.stats_label = tk.Label(
            parent, text="Meals: 0",
            font=("Courier New", 11, "bold"), fg="#333",
        )
        self.stats_label.pack(pady=2)

        self.meals = [0] * num_philosophers
        self.eating = [False] * num_philosophers
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        import math
        phil_r = max(4, min(20, 100 // max(1, self.n // 3 + 1)))
        fork_r = max(2, phil_r // 3)

        for i in range(self.n):
            angle = 2 * math.pi * i / self.n
            fx = self.center + self.radius * math.cos(angle)
            fy = self.center + self.radius * math.sin(angle)
            held = self.eating[i] or self.eating[(i - 1) % self.n]
            color = "#4CAF50" if held else "#CCCCCC"
            self.canvas.create_oval(fx - fork_r, fy - fork_r,
                                    fx + fork_r, fy + fork_r,
                                    fill=color, outline="#666")

        for i in range(self.n):
            angle = 2 * math.pi * i / self.n - math.pi / 2
            px = self.center + (self.radius - 40) * math.cos(angle)
            py = self.center + (self.radius - 40) * math.sin(angle)
            color = "#FF9800" if self.eating[i] else "#2196F3"
            self.canvas.create_oval(px - phil_r, py - phil_r,
                                    px + phil_r, py + phil_r,
                                    fill=color, outline="#333", width=2)
            if phil_r >= 12:
                self.canvas.create_text(px, py, text=f"P{i}", fill="white",
                                        font=("Courier New", max(7, phil_r // 2), "bold"))
            if phil_r >= 10:
                self.canvas.create_text(px, py + phil_r + 10, text=f"{self.meals[i]}",
                                        fill="#333", font=("Courier New", 8))

    def set_state(self, philosopher_id, is_eating, meal_count):
        self.eating[philosopher_id] = is_eating
        self.meals[philosopher_id] = meal_count
        self.draw()
        self.stats_label.config(text=f"Meals: {sum(self.meals)}")


# ============================================================
# READER-WRITER VISUALIZER
# ============================================================
class ReaderWriterVisualizer:
    """Grid of squares showing active readers/writers."""

    def __init__(self, parent, num_readers, num_writers):
        self.num_readers = num_readers
        self.num_writers = num_writers
        self.cell = 26
        self.gap = 5

        cols = max(num_readers, num_writers)
        width = min(cols * (self.cell + self.gap) + self.gap + 40, 550)
        height = 2 * (self.cell + self.gap) + 24

        self.canvas = tk.Canvas(
            parent, width=width, height=height,
            bg="white", highlightthickness=1, highlightbackground="#cccccc",
        )
        self.canvas.pack(pady=5)

        self.stats_label = tk.Label(
            parent, text="Reads: 0 | Writes: 0",
            font=("Courier New", 11, "bold"), fg="#333",
        )
        self.stats_label.pack(pady=2)

        self.reader_active = [False] * num_readers
        self.writer_active = [False] * num_writers
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_text(6, 12, text="R:", anchor="w",
                                font=("Courier New", 10, "bold"), fill="#2196F3")
        for i in range(self.num_readers):
            x = 30 + i * (self.cell + self.gap)
            y = self.gap
            color = "#2196F3" if self.reader_active[i] else "#E3F2FD"
            self.canvas.create_rectangle(x, y, x + self.cell, y + self.cell,
                                         fill=color, outline="#888")

        self.canvas.create_text(6, 12 + self.cell + self.gap + 4, text="W:",
                                anchor="w", font=("Courier New", 10, "bold"), fill="#E91E63")
        for i in range(self.num_writers):
            x = 30 + i * (self.cell + self.gap)
            y = self.gap + self.cell + self.gap + 4
            color = "#E91E63" if self.writer_active[i] else "#FCE4EC"
            self.canvas.create_rectangle(x, y, x + self.cell, y + self.cell,
                                         fill=color, outline="#888")

    def update(self, output_text):
        lines = output_text.strip().split("\n")[-30:]
        self.reader_active = [False] * self.num_readers
        self.writer_active = [False] * self.num_writers
        for line in lines:
            if "Reader" in line and "is reading" in line and "finished" not in line:
                try:
                    idx = int(line.split("Reader")[1].split()[0])
                    if idx < self.num_readers:
                        self.reader_active[idx] = True
                except Exception:
                    pass
            if "Writer" in line and "is writing" in line and "finished" not in line:
                try:
                    idx = int(line.split("Writer")[1].split()[0])
                    if idx < self.num_writers:
                        self.writer_active[idx] = True
                except Exception:
                    pass
        self.stats_label.config(
            text=f"Reads: {output_text.count('is reading')} | "
                 f"Writes: {output_text.count('is writing')}"
        )
        self.draw()


# ============================================================
# MAIN GUI
# ============================================================
class SyncMasterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SyncMaster - Thread Synchronization")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 750)

        # Speed slider row
        top = ttk.Frame(root)
        top.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(top, text="Simulation Speed:").pack(side="left", padx=(0, 8))
        self.speed_var = tk.DoubleVar(value=1.0)
        ttk.Scale(
            top, from_=0.2, to=3.0, orient="horizontal",
            variable=self.speed_var, length=200,
            command=self._on_speed_change,
        ).pack(side="left")
        self.speed_label = ttk.Label(top, text="1.0x")
        self.speed_label.pack(side="left", padx=8)

        # Control buttons row
        ctrl = ttk.Frame(root)
        ctrl.pack(fill="x", padx=10, pady=(5, 0))

        self.pause_btn = ttk.Button(ctrl, text="⏸ Pause",
                                    command=self._pause_all, state="disabled")
        self.pause_btn.pack(side="left", padx=3)

        self.resume_btn = ttk.Button(ctrl, text="▶ Resume",
                                     command=self._resume_all, state="disabled")
        self.resume_btn.pack(side="left", padx=3)

        self.stop_btn = ttk.Button(ctrl, text="⏹ Stop",
                                   command=self._stop_all, state="disabled")
        self.stop_btn.pack(side="left", padx=3)

        ttk.Button(ctrl, text="Quit", command=root.quit).pack(side="right", padx=3)

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.create_producer_consumer_tab()
        self.create_dining_philosophers_tab()
        self.create_reader_writer_tab()
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

    def _on_speed_change(self, value):
        v = float(value)
        SpeedControl.set(v)
        self.speed_label.config(text=f"{v:.1f}x")

    def _pause_all(self):
        SimulationControl.pause()
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="normal")

    def _resume_all(self):
        SimulationControl.resume()
        self.pause_btn.config(state="normal")
        self.resume_btn.config(state="disabled")

    def _stop_all(self):
        SimulationControl.stop()
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

    def _enable_controls(self):
        self.pause_btn.config(state="normal")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def _disable_controls(self):
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

    # --------------------------------------------------------
    # PRODUCER-CONSUMER TAB
    # --------------------------------------------------------
    def create_producer_consumer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Producer-Consumer")

        input_frame = ttk.LabelFrame(tab, text="Parameters", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        labels = ["Buffer Size:", "Producers:", "Consumers:", "Items per Producer:"]
        entries = []
        for i, text in enumerate(labels):
            ttk.Label(input_frame, text=text).grid(row=i, column=0, sticky="e", padx=4, pady=3)
            e = ttk.Entry(input_frame, width=12)
            e.grid(row=i, column=1, padx=4, pady=3)
            e.insert(0, "5" if i == 0 else "2" if i < 3 else "5")
            entries.append(e)
        self.buffer_size, self.num_producers, self.num_consumers, self.items_per_producer = entries

        ttk.Button(input_frame, text="Run Simulation",
                   command=self.run_producer_consumer).grid(
            row=4, column=0, columnspan=2, pady=8)

        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True)

        left_col = ttk.Frame(frame)
        left_col.pack(side="left", fill="both", expand=True)

        metrics_frame = ttk.LabelFrame(left_col, text="Live Buffer View", padding=10)
        metrics_frame.pack(fill="x", padx=(0, 10))

        self.pc_visualizer_container = ttk.Frame(metrics_frame)
        self.pc_visualizer_container.pack(fill="both", expand=True)

        self.pc_metrics = scrolledtext.ScrolledText(
            metrics_frame, font=("Courier New", 9), height=4, width=55)
        self.pc_metrics.pack(fill="both", expand=True, pady=(10, 0))

        graph_frame = ttk.LabelFrame(left_col, text="Throughput Over Time", padding=8)
        graph_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.pc_graph = ThroughputGraph(graph_frame)

        output_frame = ttk.LabelFrame(frame, text="Output", padding=8)
        output_frame.pack(side="right", fill="both", expand=False)

        self.pc_output = scrolledtext.ScrolledText(
            output_frame, wrap=tk.NONE, font=("Courier New", 9),
            width=65, height=30)
        self.pc_output.pack(fill="both", expand=True)

        h_scroll = ttk.Scrollbar(output_frame, orient="horizontal",
                                 command=self.pc_output.xview)
        h_scroll.pack(fill="x")
        self.pc_output.config(xscrollcommand=h_scroll.set)

    def run_producer_consumer(self):
        try:
            b = int(self.buffer_size.get())
            p = int(self.num_producers.get())
            c = int(self.num_consumers.get())
            i = int(self.items_per_producer.get())
            if b < 1 or p < 1 or c < 1 or i < 1:
                messagebox.showerror("Error", "All values must be >= 1")
                return
            if b > 50:
                messagebox.showerror("Error", "Max buffer size 50 for readability")
                return

            SimulationControl.init()
            self._enable_controls()

            for w in self.pc_visualizer_container.winfo_children():
                w.destroy()

            self.pc_visualizer = BufferVisualizer(
                self.pc_visualizer_container, buffer_size=b, total_items=p * i)

            self.pc_graph.reset()

            self.pc_output.delete(1.0, tk.END)
            self.pc_metrics.delete(1.0, tk.END)
            self.temp_stdout = StringIO()
            self.old_stdout = sys.stdout
            sys.stdout = self.temp_stdout
            self.pc_thread = threading.Thread(
                target=self._run_pc_sim, args=(b, p, c, i), daemon=True)
            self.pc_thread.start()
            self.update_pc_output()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def _run_pc_sim(self, b, p, c, i):
        producer_consumer.run_simulation(b, p, c, i)
        sys.stdout = self.old_stdout

    def update_pc_output(self):
        if isinstance(sys.stdout, StringIO):
            output = self.temp_stdout.getvalue()
            self.pc_output.delete(1.0, tk.END)
            self.pc_output.insert(tk.END, output)
            self.pc_output.see(tk.END)

            produced = output.count("produced")
            consumed = output.count("consumed")
            in_flight = max(0, produced - consumed)

            if hasattr(self, "pc_visualizer"):
                self.pc_visualizer.update(produced, consumed, in_flight)
            if hasattr(self, "pc_graph"):
                self.pc_graph.add_point(produced, consumed)

            self.pc_metrics.delete(1.0, tk.END)
            self.pc_metrics.insert(
                tk.END,
                f"Produced: {produced}   Consumed: {consumed}   "
                f"Buffer cap: {self.buffer_size.get()}"
            )

            if hasattr(self, "pc_thread") and not self.pc_thread.is_alive():
                sys.stdout = self.old_stdout if hasattr(self, "old_stdout") else sys.stdout
                self._disable_controls()
                return

            self.root.after(200, self.update_pc_output)

    # --------------------------------------------------------
    # DINING PHILOSOPHERS TAB
    # --------------------------------------------------------
    def create_dining_philosophers_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dining Philosophers")

        input_frame = ttk.LabelFrame(tab, text="Parameters", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Philosophers:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.num_philosophers = ttk.Entry(input_frame, width=12)
        self.num_philosophers.grid(row=0, column=1, padx=4, pady=3)
        self.num_philosophers.insert(0, "5")

        ttk.Label(input_frame, text="Eat Cycles:").grid(row=1, column=0, sticky="e", padx=4, pady=3)
        self.eat_cycles = ttk.Entry(input_frame, width=12)
        self.eat_cycles.grid(row=1, column=1, padx=4, pady=3)
        self.eat_cycles.insert(0, "3")

        ttk.Button(input_frame, text="Run Simulation",
                   command=self.run_dining_philosophers).grid(
            row=2, column=0, columnspan=2, pady=8)

        self.dp_naive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            input_frame, text="Naive mode (deadlock demo)",
            variable=self.dp_naive_var
        ).grid(row=3, column=0, columnspan=2, pady=4)

        self.dp_banner = tk.Label(
            tab, text="", bg="#ffcccc", fg="#990000",
            font=("Courier New", 11, "bold"), pady=4
        )
        self.dp_banner.pack(fill="x", padx=10)

        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True)

        left_col = ttk.Frame(frame)
        left_col.pack(side="left", fill="both", expand=True)

        metrics_frame = ttk.LabelFrame(left_col, text="Live Table View", padding=10)
        metrics_frame.pack(fill="x", padx=(0, 10))

        self.dp_visualizer_container = ttk.Frame(metrics_frame)
        self.dp_visualizer_container.pack(fill="both", expand=True)

        self.dp_metrics = scrolledtext.ScrolledText(
            metrics_frame, font=("Consolas", 9), height=4, width=55)
        self.dp_metrics.pack(fill="both", expand=True, pady=(10, 0))

        graph_frame = ttk.LabelFrame(left_col, text="Meals Over Time", padding=8)
        graph_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.dp_graph = ThroughputGraph(
            graph_frame,
            ylabel="Meals",
            label1="Total meals", color1="#FF9800",
            label2="Eating now", color2="#2196F3",
            title="Meals Over Time",
        )

        output_frame = ttk.LabelFrame(frame, text="Output", padding=8)
        output_frame.pack(side="right", fill="both", expand=False)

        self.dp_output = scrolledtext.ScrolledText(
            output_frame, wrap=tk.NONE, font=("Consolas", 9),
            width=65, height=30)
        self.dp_output.pack(fill="both", expand=True)

        h_scroll = ttk.Scrollbar(output_frame, orient="horizontal",
                                 command=self.dp_output.xview)
        h_scroll.pack(fill="x")
        self.dp_output.config(xscrollcommand=h_scroll.set)

    def run_dining_philosophers(self):
        try:
            n = int(self.num_philosophers.get())
            c = int(self.eat_cycles.get())
            if n < 2:
                messagebox.showerror("Error", "At least 2 philosophers")
                return
            if n > 20:
                messagebox.showerror("Error", "Max 20 philosophers for readability")
                return
            if c < 1:
                messagebox.showerror("Error", "Eat cycles must be >= 1")
                return

            SimulationControl.init()
            self._enable_controls()
            self.dp_banner.config(text="")
            self._dp_last_len = 0
            self._dp_last_change = _time.time()

            for w in self.dp_visualizer_container.winfo_children():
                w.destroy()

            self.dp_visualizer = PhilosopherVisualizer(
                self.dp_visualizer_container, num_philosophers=n)

            self.dp_graph.reset()

            self.dp_output.delete(1.0, tk.END)
            self.dp_metrics.delete(1.0, tk.END)
            self.temp_stdout = StringIO()
            self.old_stdout = sys.stdout
            sys.stdout = self.temp_stdout

            naive = self.dp_naive_var.get()
            self.dp_thread = threading.Thread(
                target=self._run_dp_sim, args=(n, c, naive), daemon=True)
            self.dp_thread.start()
            self.update_dp_output()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def _run_dp_sim(self, n, c, naive):
        try:
            dining_philosopher.run_simulation(n, c, naive=naive)
        finally:
            sys.stdout = self.old_stdout

    def update_dp_output(self):
        if isinstance(sys.stdout, StringIO):
            output = self.temp_stdout.getvalue()

            if len(output) != self._dp_last_len:
                self._dp_last_len = len(output)
                self._dp_last_change = _time.time()

            self.dp_output.delete(1.0, tk.END)
            self.dp_output.insert(tk.END, output)
            self.dp_output.see(tk.END)

            meals = output.count("is eating")
            n_phil = int(self.num_philosophers.get())

            recent = output.strip().split("\n")[-40:]
            eating_now = 0
            for line in recent:
                if "is eating" in line and "released" not in line:
                    eating_now += 1
            eating_now = min(eating_now, n_phil)

            self.dp_metrics.delete(1.0, tk.END)
            self.dp_metrics.insert(
                tk.END,
                f"Meals served: {meals}   Philosophers: {self.num_philosophers.get()}"
            )

            if hasattr(self, "dp_graph"):
                self.dp_graph.add_point(meals, eating_now)

            if (self.dp_naive_var.get()
                    and hasattr(self, "dp_thread")
                    and self.dp_thread.is_alive()
                    and _time.time() - self._dp_last_change > 3.0):
                if self.dp_banner.cget("text") == "":
                    self.dp_banner.config(
                        text="⚠ DEADLOCK DETECTED — all philosophers stuck waiting for forks"
                    )

            if hasattr(self, "dp_thread") and not self.dp_thread.is_alive():
                sys.stdout = self.old_stdout if hasattr(self, "old_stdout") else sys.stdout
                self._disable_controls()
                return

            self.root.after(200, self.update_dp_output)

    # --------------------------------------------------------
    # READER-WRITER TAB
    # --------------------------------------------------------
    def create_reader_writer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reader-Writer")

        input_frame = ttk.LabelFrame(tab, text="Parameters", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        fields = [
            ("Readers:", "num_readers", "3"),
            ("Writers:", "num_writers", "2"),
            ("Read Ops:", "read_ops", "3"),
            ("Write Ops:", "write_ops", "2"),
        ]
        for i, (label, attr, default) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky="e", padx=4, pady=3)
            e = ttk.Entry(input_frame, width=12)
            e.grid(row=i, column=1, padx=4, pady=3)
            e.insert(0, default)
            setattr(self, attr, e)

        ttk.Button(input_frame, text="Run Simulation",
                   command=self.run_reader_writer).grid(
            row=4, column=0, columnspan=2, pady=8)

        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True)

        left_col = ttk.Frame(frame)
        left_col.pack(side="left", fill="both", expand=True)

        metrics_frame = ttk.LabelFrame(left_col, text="Live Activity View", padding=10)
        metrics_frame.pack(fill="x", padx=(0, 10))

        self.rw_visualizer_container = ttk.Frame(metrics_frame)
        self.rw_visualizer_container.pack(fill="both", expand=True)

        self.rw_metrics = scrolledtext.ScrolledText(
            metrics_frame, font=("Consolas", 9), height=4, width=55)
        self.rw_metrics.pack(fill="both", expand=True, pady=(10, 0))

        graph_frame = ttk.LabelFrame(left_col, text="Reads / Writes Over Time", padding=8)
        graph_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.rw_graph = ThroughputGraph(
            graph_frame,
            ylabel="Ops",
            label1="Reads", color1="#2196F3",
            label2="Writes", color2="#E91E63",
            title="Reads vs Writes Over Time",
        )

        output_frame = ttk.LabelFrame(frame, text="Output", padding=8)
        output_frame.pack(side="right", fill="both", expand=False)

        self.rw_output = scrolledtext.ScrolledText(
            output_frame, wrap=tk.NONE, font=("Consolas", 9),
            width=65, height=30)
        self.rw_output.pack(fill="both", expand=True)

        h_scroll = ttk.Scrollbar(output_frame, orient="horizontal",
                                 command=self.rw_output.xview)
        h_scroll.pack(fill="x")
        self.rw_output.config(xscrollcommand=h_scroll.set)

    def run_reader_writer(self):
        try:
            r = int(self.num_readers.get())
            w = int(self.num_writers.get())
            ro = int(self.read_ops.get())
            wo = int(self.write_ops.get())
            if min(r, w, ro, wo) < 1:
                messagebox.showerror("Error", "All values must be >= 1")
                return
            if max(r, w) > 30:
                messagebox.showerror("Error", "Max 30 readers/writers for readability")
                return

            SimulationControl.init()
            self._enable_controls()

            for widget in self.rw_visualizer_container.winfo_children():
                widget.destroy()

            self.rw_visualizer = ReaderWriterVisualizer(
                self.rw_visualizer_container, num_readers=r, num_writers=w)

            self.rw_graph.reset()

            self.rw_output.delete(1.0, tk.END)
            self.rw_metrics.delete(1.0, tk.END)
            self.temp_stdout = StringIO()
            self.old_stdout = sys.stdout
            sys.stdout = self.temp_stdout
            self.rw_thread = threading.Thread(
                target=self._run_rw_sim, args=(r, w, ro, wo), daemon=True)
            self.rw_thread.start()
            self.update_rw_output()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def _run_rw_sim(self, r, w, ro, wo):
        reader_writer.run_simulation(r, w, ro, wo)
        sys.stdout = self.old_stdout

    def update_rw_output(self):
        if isinstance(sys.stdout, StringIO):
            output = self.temp_stdout.getvalue()
            self.rw_output.delete(1.0, tk.END)
            self.rw_output.insert(tk.END, output)
            self.rw_output.see(tk.END)

            if hasattr(self, "rw_visualizer"):
                self.rw_visualizer.update(output)

            reads = output.count("is reading")
            writes = output.count("is writing")

            if hasattr(self, "rw_graph"):
                self.rw_graph.add_point(reads, writes)

            self.rw_metrics.delete(1.0, tk.END)
            self.rw_metrics.insert(tk.END, f"Reads: {reads}   Writes: {writes}")

            if hasattr(self, "rw_thread") and not self.rw_thread.is_alive():
                sys.stdout = self.old_stdout if hasattr(self, "old_stdout") else sys.stdout
                self._disable_controls()
                return

            self.root.after(200, self.update_rw_output)


if __name__ == "__main__":
    root = tk.Tk()
    app = SyncMasterGUI(root)
    root.mainloop()
                                   