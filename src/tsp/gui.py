import itertools
import math
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional

from tsp.algorithms.constructive import cheapest_insertion, nearest_neighbor, three_opt, two_opt
from tsp.io.csv_reader import read_asymetric_matrix
from tsp.models.graph import AsymmetricGraph

try:
    import matplotlib

    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None  # type: ignore
    FigureCanvasTkAgg = None  # type: ignore
    MATPLOTLIB_AVAILABLE = False


class TSPGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TSP Solver")
        self.geometry("1200x800")
        self.resizable(True, True)

        # Variables
        self.csv_file = tk.StringVar()
        self.algorithm = tk.StringVar(value="nearest_neighbor")
        self.start = tk.IntVar(value=0)
        self.two_opt = tk.BooleanVar()
        self.two_opt_max_passes = tk.IntVar(value=100)
        self.two_opt_timeout = tk.DoubleVar()
        self.three_opt = tk.BooleanVar()
        self.three_opt_max_passes = tk.IntVar(value=100)
        self.three_opt_timeout = tk.DoubleVar()
        self.benchmark = tk.BooleanVar()
        self.runs = tk.IntVar(value=10)

        # Graph and table
        self.graph: Optional[AsymmetricGraph] = None
        self.table_entries: list[list[tk.Entry]] = []
        self.labels: list[str] = []

        # Layout
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Settings Tab
        self.settings_frame = tk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")

        # CSV File
        tk.Label(self.settings_frame, text="CSV File:").grid(row=0, column=0, sticky="w")
        tk.Entry(self.settings_frame, textvariable=self.csv_file, width=30).grid(row=0, column=1)
        tk.Button(self.settings_frame, text="Browse", command=self.browse_file).grid(
            row=0, column=2
        )
        tk.Button(self.settings_frame, text="Load Table", command=self.load_table).grid(
            row=0, column=3
        )

        # Algorithm
        tk.Label(self.settings_frame, text="Algorithm:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(
            self.settings_frame,
            textvariable=self.algorithm,
            values=["nearest_neighbor", "cheapest_insertion"],
            width=15,
        ).grid(row=1, column=1)

        # Start
        tk.Label(self.settings_frame, text="Start Node:").grid(row=2, column=0, sticky="w")
        tk.Entry(self.settings_frame, textvariable=self.start, width=5).grid(row=2, column=1)

        # 2-opt
        tk.Checkbutton(self.settings_frame, text="2-opt", variable=self.two_opt).grid(
            row=3, column=0, sticky="w"
        )
        tk.Label(self.settings_frame, text="Max Passes:").grid(row=4, column=0, sticky="w")
        tk.Entry(self.settings_frame, textvariable=self.two_opt_max_passes, width=5).grid(
            row=4, column=1
        )
        tk.Label(self.settings_frame, text="Timeout (s):").grid(row=5, column=0, sticky="w")
        tk.Entry(self.settings_frame, textvariable=self.two_opt_timeout, width=5).grid(
            row=5, column=1
        )

        # 3-opt
        tk.Checkbutton(self.settings_frame, text="3-opt", variable=self.three_opt).grid(
            row=6, column=0, sticky="w"
        )
        tk.Label(self.settings_frame, text="Max Passes:").grid(row=7, column=0, sticky="w")
        tk.Entry(self.settings_frame, textvariable=self.three_opt_max_passes, width=5).grid(
            row=7, column=1
        )
        tk.Label(self.settings_frame, text="Timeout (s):").grid(row=8, column=0, sticky="w")
        tk.Entry(self.settings_frame, textvariable=self.three_opt_timeout, width=5).grid(
            row=8, column=1
        )

        # Benchmark
        tk.Checkbutton(self.settings_frame, text="Benchmark", variable=self.benchmark).grid(
            row=9, column=0, sticky="w"
        )
        tk.Label(self.settings_frame, text="Runs:").grid(row=10, column=0, sticky="w")
        tk.Entry(self.settings_frame, textvariable=self.runs, width=5).grid(row=10, column=1)

        # Data Table Tab
        self.table_frame = tk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Data Table")

        # Scrollable canvas for table
        self.table_canvas = tk.Canvas(self.table_frame)
        self.table_scrollbar_v = tk.Scrollbar(self.table_frame, orient="vertical", command=self.table_canvas.yview)
        self.table_scrollbar_h = tk.Scrollbar(self.table_frame, orient="horizontal", command=self.table_canvas.xview)
        self.table_canvas.configure(yscrollcommand=self.table_scrollbar_v.set, xscrollcommand=self.table_scrollbar_h.set)

        self.table_canvas.pack(side="left", fill="both", expand=True)
        self.table_scrollbar_v.pack(side="right", fill="y")
        self.table_scrollbar_h.pack(side="bottom", fill="x")

        self.table_inner_frame = tk.Frame(self.table_canvas)
        self.table_canvas.create_window((0, 0), window=self.table_inner_frame, anchor="nw")

        self.table_inner_frame.bind("<Configure>", lambda e: self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all")))
        # Bind mouse wheel
        self.table_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.table_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.table_canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Graph View Tab
        self.graph_frame = tk.Frame(self.notebook)
        self.notebook.add(self.graph_frame, text="Graph View")

        # Results in Graph tab
        self.result_text = tk.Text(self.graph_frame, height=10, width=80)
        self.result_text.pack(side=tk.BOTTOM, fill=tk.X)

        # Plot
        if MATPLOTLIB_AVAILABLE:
            self.figure = plt.Figure(figsize=(5, 4), dpi=100)  # type: ignore
            self.ax = self.figure.add_subplot(111)
            self.ax.axis("off")
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)  # type: ignore
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            tk.Label(self.graph_frame, text="Matplotlib not available for plotting").pack()

        # Progress Bar and Run Button
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.run_button = tk.Button(self.main_frame, text="Run TSP", command=self.run_tsp)
        self.run_button.pack(side=tk.BOTTOM, pady=10)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file:
            self.csv_file.set(file)

    def load_table(self):
        try:
            self.graph = read_asymetric_matrix(self.csv_file.get())
            self.labels = self.graph.labels
            self.create_table()
            self.plot_nodes(self.graph)
            self.notebook.select(1)  # Switch to Data Table tab
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error loading table: {e}")

    def create_table(self):
        if self.graph is None:
            return
        # Clear existing table
        for widget in self.table_inner_frame.winfo_children():
            widget.destroy()
        self.table_entries = []

        n = self.graph.n
        # Headers
        tk.Label(self.table_inner_frame, text="", width=5).grid(row=0, column=0)  # Corner
        for j in range(n):
            tk.Label(self.table_inner_frame, text=self.labels[j], width=5).grid(row=0, column=j + 1)
        for i in range(n):
            tk.Label(self.table_inner_frame, text=self.labels[i], width=5).grid(row=i + 1, column=0)
            row_entries = []
            for j in range(n):
                entry = tk.Entry(self.table_inner_frame, width=5)
                if i == j:
                    entry.insert(0, "inf")
                    entry.config(state="disabled")
                else:
                    entry.insert(0, str(self.graph.c(i, j)))
                entry.grid(row=i + 1, column=j + 1)
                row_entries.append(entry)
            self.table_entries.append(row_entries)
        # Update scroll region
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        if event.delta:
            self.table_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:
            self.table_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.table_canvas.yview_scroll(1, "units")

    def get_graph_from_table(self) -> AsymmetricGraph:
        if not self.table_entries:
            raise ValueError("Table not loaded")
        n = len(self.table_entries)
        cost_matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(float("inf"))
                else:
                    val = self.table_entries[i][j].get().strip()
                    if val in ["", "inf", "NA"]:
                        row.append(float("inf"))
                    else:
                        row.append(float(val))
            cost_matrix.append(row)
        return AsymmetricGraph(cost_matrix, self.labels)

    def start_progress(self):
        self.progress.pack(side=tk.BOTTOM, pady=5, before=self.run_button)
        self.progress.start()
        self.run_button.config(state='disabled')

    def stop_progress(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.run_button.config(state='normal')

    def run_tsp(self):
        self.start_progress()
        thread = threading.Thread(target=self._run_computation)
        thread.start()

    def _run_computation(self):
        try:
            if self.table_entries:
                graph = self.get_graph_from_table()
            else:
                graph = read_asymetric_matrix(self.csv_file.get())
            algos = {"nearest_neighbor": nearest_neighbor, "cheapest_insertion": cheapest_insertion}

            def get_tour_cost(start):
                tour, cost = algos[self.algorithm.get()](graph, start)
                if self.two_opt.get():
                    timeout = self.two_opt_timeout.get() if self.two_opt_timeout.get() > 0 else None
                    tour, cost = two_opt(
                        graph, tour, max_passes=self.two_opt_max_passes.get(), timeout=timeout
                    )
                if self.three_opt.get():
                    timeout = (
                        self.three_opt_timeout.get() if self.three_opt_timeout.get() > 0 else None
                    )
                    tour, cost = three_opt(
                        graph, tour, max_passes=self.three_opt_max_passes.get(), timeout=timeout
                    )
                return tour, cost

            if self.benchmark.get():
                costs = []
                times = []
                tour = []
                for _ in range(self.runs.get()):
                    start_time = time.time()
                    tour, cost = get_tour_cost(self.start.get())
                    end_time = time.time()
                    costs.append(cost)
                    times.append(end_time - start_time)
                algo_name = (
                    f"{self.algorithm.get()}"
                    f"{' + 2-opt' if self.two_opt.get() else ''}"
                    f"{' + 3-opt' if self.three_opt.get() else ''}"
                )
                avg_cost = sum(costs) / len(costs)
                avg_time = sum(times) / len(times)
                result = (
                    f"Algorithm: {algo_name}\nRuns: {self.runs.get()}\n"
                    f"Cost - Min: {min(costs):.2f}, Max: {max(costs):.2f}, Avg: {avg_cost:.2f}\n"
                    f"Time - Min: {min(times):.4f}s, Max: {max(times):.4f}s, Avg: {avg_time:.4f}s"
                )
                self.after(0, lambda: self._on_computation_done(graph, tour, result))
            else:
                tour, cost = get_tour_cost(self.start.get())
                tour_labels = [graph.labels[i] for i in tour]
                result = f"Tour: {tour_labels}\nCost: {cost}"
                self.after(0, lambda: self._on_computation_done(graph, tour, result))
        except Exception as e:
            self.after(0, lambda: self._on_error(e))

    def _on_computation_done(self, graph, tour, result):
        self.stop_progress()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.plot_tour(graph, tour)
        self.notebook.select(2)  # Switch to Graph View tab

    def _on_error(self, e):
        self.stop_progress()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Error: {e}")

    def plot_nodes(self, graph):
        self.plot_tour(graph, None)

    def plot_tour(self, graph, tour):
        if not MATPLOTLIB_AVAILABLE:
            return
        self.ax.clear()
        n = graph.n
        angles = [2 * math.pi * i / n for i in range(n)]
        x = [math.cos(a) for a in angles]
        y = [math.sin(a) for a in angles]
        self.ax.scatter(x, y, c="blue")
        for i, label in enumerate(graph.labels):
            self.ax.text(x[i], y[i], label, fontsize=12, ha="center", va="center")
        if tour:
            tour_x = [x[i] for i in tour] + [x[tour[0]]]
            tour_y = [y[i] for i in tour] + [y[tour[0]]]
            self.ax.plot(tour_x, tour_y, "r-")
        self.ax.axis("off")  # Remove axis labels and ticks
        self.canvas.draw()


def main():
    try:
        app = TSPGUI()
        app.mainloop()
    except Exception as e:
        print(f"GUI failed to start: {e}")
        print("Try running in a graphical environment or with xvfb-run.")
